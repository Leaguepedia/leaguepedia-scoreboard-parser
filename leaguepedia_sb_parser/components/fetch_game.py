from bayes_lol_client import BayesEMH
from riotwatcher import LolWatcher
import riot_transmute

import os
import json

from mwrogue.esports_client import EsportsClient


def get_game_from_wiki(game, site: EsportsClient):
    try:
        summary, details = site.get_data_and_timeline(game, 5)
    except KeyError:
        summary, details = site.get_data_and_timeline(game, 4)
    return cast_game(summary, details)


def get_bayes_game(game):
    emh = BayesEMH()
    summary, details = emh.get_game_data(game)
    return cast_game(summary, details)


def get_riot_api_key():
    config_path = os.path.join(os.path.expanduser("~"), ".config", "leaguepedia_sb_parser")
    keys_file = os.path.join(config_path, "keys.json")
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    if not os.path.isfile(keys_file):
        print("The Riot API Key was not found")
        riot_api_key = input("Riot API key: ")
        with open(file=keys_file, mode="w+", encoding="utf8") as f:
            json.dump(
                {"riot_api_key": riot_api_key}, f, ensure_ascii=False
            )
    with open(file=keys_file, mode="r+", encoding="utf8") as f:
        riot_api_key = json.load(f)["riot_api_key"]
    return riot_api_key


def get_live_game(game):
    lol_watcher = LolWatcher(get_riot_api_key())
    region = game.split("_")[0]
    summary, details = lol_watcher.match.by_id(
        region, game
    ), lol_watcher.match.timeline_by_match(region, game)
    return cast_game(summary["info"], details["info"])


def cast_game(game_summary, game_details):
    game_dto_summary = riot_transmute.v5.match_to_game(game_summary)
    game_dto_details = riot_transmute.v5.match_timeline_to_game(game_details)
    return riot_transmute.merge_games_from_riot_match_and_timeline(
        game_dto_summary, game_dto_details
    )
