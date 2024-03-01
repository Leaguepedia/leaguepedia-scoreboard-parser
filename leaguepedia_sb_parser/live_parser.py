from leaguepedia_sb_parser.components.fetch_game import get_live_game
from leaguepedia_sb_parser.parser import Parser


class LiveParser(Parser):
    statslink = "rpgid"
    version = 5

    SERVER_TO_REGION = {
        "NA1": "AMERICAS",
        "BR1": "AMERICAS",
        "LA1": "AMERICAS",
        "LA2": "AMERICAS",
        "OC1": "AMERICAS",
        "KR": "ASIA",
        "VN": "ASIA",
        "VN1": "ASIA",
        "JP1": "ASIA",
        "EUN1": "EUROPE",
        "EUW1": "EUROPE",
        "TR1": "EUROPE",
        "RU": "EUROPE",
        "PH2": "SEA",
        "SG2": "SEA",
        "TH2": "SEA",
        "TW2": "SEA",
        "VN2": "SEA",
    }

    def query_rpgid(self, platform_game_id):
        result = self.site.cargo_client.query(
            tables="MatchScheduleGame=MSG, Tournaments=T, MatchSchedule=MS",
            join_on="MSG.OverviewPage=T.OverviewPage, MSG.MatchId=MS.MatchId",
            fields="T.StandardName=Event, MSG.Blue=Blue, MSG.Red=Red, MS.Patch=Patch",
            where='MSG.RiotPlatformGameId = "{}"'.format(platform_game_id),
        )
        if len(result) == 0:
            self.warnings.append("Could not determine teams from wiki!")
            return {"Blue": None, "Red": None}
        return result[0]

    def determine_teams_from_wiki(self, platform_game_id):
        result = self.query_rpgid(platform_game_id)
        self.save_teams(result["Blue"], result["Red"])

    def parse_series(self, match, header=True):
        output_parts = []
        warnings = []
        for game in match:
            game_output, game_warnings = self.parse_game(game.strip())
            output_parts.append(game_output)
            warnings.extend(game_warnings)
        if header:
            output_parts.insert(0, self.make_match_header())
        return "\n".join(output_parts), warnings

    def get_initial_team_name(self, team):
        tricode = team.players[0].inGameName.split(" ")[0]
        return tricode

    def get_player_ingame_name(self, player, team_name):
        return player.inGameName

    def parse_game(self, platform_game_id):
        game = get_live_game(platform_game_id)
        self.determine_teams_from_wiki(platform_game_id)
        output = self.parse_one_game(
            game, platform_game_id, key="riot_platform_game_id"
        )
        warnings = self.warnings
        self.clear_warnings()
        return output, warnings

    @staticmethod
    def is_live_server(url: str) -> bool:
        if LiveParser.SERVER_TO_REGION.get(url.split("_")[0]) is not None:
            return True
        return False

    def get_checksum(self, game):
        return None
