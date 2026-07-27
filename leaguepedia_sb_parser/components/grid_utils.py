import requests
import backoff
import os

from .errors import RiotGameNotFound, TencentGameNotFound


class RateLimitException(Exception):
	pass


class NotFoundException(Exception):
	pass


def get_riot_game_data_by_platform_game_id(platform_game_id):
	def _get_file(series_id, game_sequence, file_type):
		return _make_request(
			"GET",
			f"file-download/end-state/riot/series/{series_id}/games/{game_sequence}/{file_type}"
		)

	game_id_by_external_id_query = """
	query GameIDByExternalID($dataProviderName: String!, $externalGameId: ID!) {
		gameIdByExternalId(
			dataProviderName: $dataProviderName
			externalGameId: $externalGameId
		)
	}
	"""
	game_id_by_external_id = _make_request("POST", "central-data/graphql", data={
		"query": game_id_by_external_id_query,
		"variables": {
			"dataProviderName": "LOL_LIVE",
			"externalGameId": platform_game_id
		}
	})["data"].get("gameIdByExternalId")

	if not game_id_by_external_id:
		raise RiotGameNotFound(platform_game_id)

	series_query = """
	query GetSeries($gameId: [ID!]) {
		allSeries (
			first: 1
			filter: {
				titleId: 3
				type: ESPORTS
				live: {
					games: {
						id: {
							in: $gameId
						}
					}
				}
			}
		) {
			edges {
				node {
					id
				}
			}
		}
	}
	"""

	series_results = _make_request("POST", "central-data/graphql", data={
		"query": series_query,
		"variables": {
			"gameId": [game_id_by_external_id]
		}
	})["data"]["allSeries"]["edges"]

	if not series_results:
		raise RiotGameNotFound(platform_game_id)

	series_id = series_results[0]["node"]["id"]

	file_list = _make_request("GET", f"file-download/list/{series_id}")["files"]

	summary, details = None, None

	for file_data in file_list:
		if file_data["status"] != "ready" or not file_data["id"].startswith("state-summary-riot"):
			continue
		game_sequence = file_data["id"].split("-")[-1]
		summary = _get_file(series_id, game_sequence, "summary")
		if f"{summary['platformId']}_{summary['gameId']}" != platform_game_id:
			continue
		details = _get_file(series_id, game_sequence, "details")
		break

	if not summary:
		raise RiotGameNotFound(platform_game_id)

	return summary, details


def get_tencent_series_data_by_series_id(series_id):
	def _get_file(series_id, game_sequence):
		return _make_request(
			"GET",
			f"file-download/end-state/tencent/series/{series_id}/games/{game_sequence}"
		)

	file_list = _make_request("GET", f"file-download/list/{series_id}")["files"]

	game_datas = []

	last_sequence = 0

	for file_data in file_list:
		if file_data["status"] != "ready" or not file_data["id"].startswith("state-tencent"):
			continue
		game_sequence = file_data["id"].split("-")[-1]
		if str(last_sequence + 1) != game_sequence:
			raise TencentGameNotFound(series_id, last_sequence + 1)
		last_sequence = int(game_sequence)
		game_data = _get_file(series_id, game_sequence)
		game_datas.append(game_data)

	ret = {
		"data": {
			"teamAId": game_datas[0]["teamAId"],
			"teamBId": game_datas[0]["teamBId"],
			"teamAScore": 0,
			"teamBScore": 0,
			"matchInfos": game_datas,
			"gridSeriesId": series_id
		}
	}

	g1t1 = game_datas[0]["teamInfos"][0]
	g1t1p1 = g1t1["playerInfos"][0]
	g1t2 = game_datas[0]["teamInfos"][1]
	g1t2p1 = g1t2["playerInfos"][0]

	if g1t1["teamId"] == ret["data"]["teamAId"]:
		ret["data"]["teamAName"] = g1t1p1["playerName"][:3]
		ret["data"]["teamBName"] = g1t2p1["playerName"][:3]
	else:
		ret["data"]["teamAName"] = g1t2p1["playerName"][:3]
		ret["data"]["teamBName"] = g1t1p1["playerName"][:3]

	for game in game_datas:
		if game["matchWin"] == ret["data"]["teamAId"]:
			ret["data"]["teamAScore"] += 1
		else:
			ret["data"]["teamBScore"] += 1

	if ret["data"]["teamAScore"] > ret["data"]["teamBScore"]:
		ret["data"]["matchWin"] = ret["data"]["teamAId"]
	else:
		ret["data"]["matchWin"] = ret["data"]["teamBId"]

	return ret


def _get_headers():
	return {
        "x-api-key": os.environ["GRID_API_KEY"],
        "Accept": "application/json",
    }


@backoff.on_exception(backoff.expo, (RateLimitException, NotFoundException), logger=None, max_time=60)
def _make_request(method, endpoint, data=None):
	base_url = "https://api.grid.gg/"

	if method == "GET":
		response = requests.get(base_url + endpoint, headers=_get_headers())
	else:
		response = requests.post(base_url + endpoint, headers=_get_headers(), json=data)

	if response.status_code in (403, 404):
		raise NotFoundException
	elif response.status_code == 429:
		raise RateLimitException
	elif "application/json" in response.headers.get("content-type", ""):
		response_j = response.json()
		if (
				response_j.get("errors") and
				response_j["errors"][0].get("extensions") and
				response_j["errors"][0]["extensions"].get("errorDetail") == "ENHANCE_YOUR_CALM"
		):
			raise RateLimitException

	return response.json()
