from leaguepedia_sb_parser.components.fetch_game import get_bayes_game, get_game_from_wiki
from leaguepedia_sb_parser.parser import Parser


class BayesParser(Parser):
    statslink = "rpgid"
    version = 5

    def get_player_ingame_name(self, player, team_name):
        ingame_name = player.inGameName
        if ingame_name is None:
            return None
        return " ".join(ingame_name.strip().split(" ")[1:]).strip()

    def get_checksum(self, game):
        return None

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

    def parse_game(self, platform_game_id):
        if self.use_leaguepedia_mirror:
            game = get_game_from_wiki(platform_game_id, self.site)
        else:
            game = get_bayes_game(platform_game_id)
        self.populate_teams(game)
        output = self.parse_one_game(
            game, platform_game_id, key="riot_platform_game_id"
        )
        warnings = self.warnings
        self.clear_warnings()
        return output, warnings
