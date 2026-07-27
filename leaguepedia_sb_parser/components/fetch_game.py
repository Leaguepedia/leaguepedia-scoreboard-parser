from riotwatcher import LolWatcher
import riot_transmute
from lol_qq_parser.parsers.match_detail import get_series_basic_info
import os
from mwrogue.esports_client import EsportsClient
from .grid_utils import get_riot_game_data_by_platform_game_id, get_tencent_series_data_by_series_id


def get_riot_game_from_wiki(platform_game_id, site: EsportsClient):
    try:
        summary, details = site.get_data_and_timeline(platform_game_id, 5)
    except KeyError:
        summary, details = site.get_data_and_timeline(platform_game_id, 4)
    return cast_game(summary, details)


def get_riot_game_from_grid(platform_game_id):
    summary, details = get_riot_game_data_by_platform_game_id(platform_game_id)

    return cast_game(summary, details)


def get_tencent_series_from_grid(series_id):
    return get_series_basic_info(get_tencent_series_data_by_series_id(series_id))


def get_riot_game_from_live(platform_game_id):
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
