import re

from leaguepedia_sb_parser.parser import Parser
from leaguepedia_sb_parser.components.fetch_game import get_tencent_series_from_grid

from mwrogue.esports_client import EsportsClient


class QQParser(Parser):
    statslink = "grid_series_id"

    initial_name_cache = {}

    def parse_series(self, series_id, include_header=True):
        series = get_tencent_series_from_grid(series_id)
        self.patch = self.get_patch(series_id)
        output_parts = []
        warnings = []
        for _, game in enumerate(series.games):
            self.populate_teams(game)
            output_parts.append(self.parse_one_game(game, series_id, key="grid_series_id"))
            warnings.extend(self.warnings)
            self.clear_warnings()
        if include_header:
            output_parts.insert(0, self.make_match_header())
        return "\n".join(output_parts), warnings

    def parse_game(self, url):
        pass

    def get_player_ingame_name(self, player, team_name):
        # remove all hanzi characters from team_name
        # these are like random city names added at the start of the name in 2021 season
        team_name = re.search(r"[A-Za-z0-9 \.]*$", team_name)[0]
        ingame_name = player.inGameName
        if re.search(r"^" + team_name, ingame_name.strip()):
            return re.sub(r"^" + team_name, "", ingame_name.strip())
        if re.search(r"^" + team_name.replace(".", ""), ingame_name.strip()):
            return re.sub(r"^" + team_name.replace(".", ""), "", ingame_name.strip())
        return player.sources.qq.name

    def get_initial_team_name(self, team):
        team_qq_id = team.sources.qq.id

        if team_qq_id in self.initial_name_cache:
            return self.initial_name_cache[team_qq_id]

        response = self.site.cargo_client.query(
            tables="Teamnames=TN",
            fields="TN.Short",
            where=f"TN.QQId = {team_qq_id}",
            limit=1,
        )
        self.initial_name_cache[team_qq_id] = response[0]["Short"]
        return self.initial_name_cache[team_qq_id]

    def get_patch(self, series_id):
        response = self.site.cargo_client.query(
            tables="MatchSchedule=MS",
            fields="MS.LegacyPatch=Patch",
            where=f"MS.GridSeriesId = '{series_id}'",
            limit=1,
        )
        if response and response[0]["Patch"] is not None:
            self.warnings.append("Patch was obtained from MatchSchedule!")
            return response[0]["Patch"]
        else:
            return None

    def get_resolved_patch(self, patch):
        # whatever we get from the game is gonna be completely garbage
        return self.patch
