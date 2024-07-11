import requests
from riotwatcher import LolWatcher
import riot_transmute

import os

from .errors import GameNotFound

from mwrogue.esports_client import EsportsClient


def get_game_from_wiki(platform_game_id, site: EsportsClient):
    try:
        summary, details = site.get_data_and_timeline(platform_game_id, 5)
    except KeyError:
        summary, details = site.get_data_and_timeline(platform_game_id, 4)
    return cast_game(summary, details)


# TODO: Move this to an external library
def get_game_from_grid(platform_game_id):
    def get_file(series_id, game_sequence, file_type):
        return requests.get(
            f"https://api.grid.gg/file-download/end-state/riot/series/{series_id}/games/{game_sequence}/{file_type}",
            headers=headers
        ).json()

    headers = {
        "x-api-key": os.environ["GRID_API_KEY"],
        "Accept": "application/json",
    }

    game_id_by_external_id_query = """
    query GameIDByExternalID($dataProviderName: String!, $externalGameId: ID!) {
        gameIdByExternalId(
            dataProviderName: $dataProviderName
            externalGameId: $externalGameId
        )
    }
    """
    game_id_by_external_id = requests.post("https://api.grid.gg/central-data/graphql", json={
        "query": game_id_by_external_id_query,
        "variables": {
            "dataProviderName": "LOL_LIVE",
            "externalGameId": platform_game_id
        }
    }, headers=headers).json()["data"].get("gameIdByExternalId")

    if not game_id_by_external_id:
        raise GameNotFound(platform_game_id)

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

    series_results = requests.post("https://api.grid.gg/central-data/graphql", json={
        "query": series_query,
        "variables": {
            "gameId": [game_id_by_external_id]
        }
    }, headers=headers).json()["data"]["allSeries"]["edges"]

    if not series_results:
        raise GameNotFound(platform_game_id)

    series_id = series_results[0]["node"]["id"]

    file_list = requests.get(f"https://api.grid.gg/file-download/list/{series_id}", headers=headers).json()["files"]

    summary, details = None, None

    for file_data in file_list:
        if file_data["status"] != "ready" or not file_data["id"].startswith("state-summary-riot"):
            continue
        game_sequence = file_data["id"].split("-")[-1]
        summary = get_file(series_id, game_sequence, "summary")
        if f"{summary['platformId']}_{summary['gameId']}" != platform_game_id:
            continue
        details = get_file(series_id, game_sequence, "details")
        break

    if not summary:
        raise GameNotFound(platform_game_id)

    return cast_game(summary, details)


def get_live_game(platform_game_id):
    lol_watcher = LolWatcher(os.environ["RIOT_API_KEY"])
    region = platform_game_id.split("_")[0]
    summary, details = lol_watcher.match.by_id(
        region, platform_game_id
    ), lol_watcher.match.timeline_by_match(region, platform_game_id)
    return cast_game(summary["info"], details["info"])


def cast_game(game_summary, game_details):
    game_dto_summary = riot_transmute.v5.match_to_game(game_summary)
    game_dto_details = riot_transmute.v5.match_timeline_to_game(game_details)
    return riot_transmute.merge_games_from_riot_match_and_timeline(
        game_dto_summary, game_dto_details
    )
