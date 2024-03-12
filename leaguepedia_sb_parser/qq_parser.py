import re

from lol_qq_parser.parsers.match_detail import get_series_basic_info

from leaguepedia_sb_parser.parser import Parser

from mwrogue.esports_client import EsportsClient


class QQParser(Parser):
    def parse_series(self, match_id, include_header=True):
        match_id = int(match_id)
        series = get_series_basic_info(match_id)
        self.patch = self.get_patch(match_id)
        output_parts = []
        warnings = []
        for i, game in enumerate(series.games):
            self.populate_teams(game)
            output_parts.append(self.parse_one_game(game, self.qq_url(match_id)))
            warnings.extend(self.warnings)
            self.clear_warnings()
        if include_header:
            output_parts.insert(0, self.make_match_header())
        return "\n".join(output_parts), warnings

    @staticmethod
    def qq_url(match_id):
        return "https://lpl.qq.com/es/stats.shtml?bmid={}".format(str(match_id))

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
        if not hasattr(team.sources, "qq"):
            return None
        return team.sources.qq.tag.strip()

    def get_patch(self, match_id):
        site = EsportsClient("lol")
        response = site.cargo_client.query(
            tables="MatchScheduleGame=MSG, MatchSchedule=MS",
            fields="MS.Patch",
            where=f"MSG.MatchHistory = 'https://lpl.qq.com/es/stats.shtml?bmid={match_id}'",
            limit=1,
            join_on="MSG.MatchId=MS.MatchId",
        )
        if response and response[0]["Patch"] is not None:
            self.warnings.append("Patch was obtained from MatchSchedule!")
            return response[0]["Patch"]
        else:
            return None

    def get_resolved_patch(self, patch):
        # whatever we get from the game is gonna be completely garbage
        return self.patch
