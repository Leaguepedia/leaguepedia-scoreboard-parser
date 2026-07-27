class EventCannotBeLocated(KeyError):
    def __str__(self):
        return "The event page for this game cannot be located!"


class InvalidGameSource(ValueError):
    def __init__(self, source):
        self.source = source

    def __str__(self):
        return f"{self.source} is not a valid source!"


class InvalidInput(ValueError):
    def __str__(self):
        return "The input format is invalid!"


class RiotGameNotFound(Exception):
    def __init__(self, game_id):
        self.game_id = game_id

    def __str__(self):
        return f"The game data for {self.game_id} could not be found!"


class TencentGameNotFound(Exception):
    def __init__(self, series_id, game_sequence):
        self.series_id = series_id
        self.game_sequence = game_sequence

    def __str__(self):
        return f"Game data for series {self.series_id} game {self.game_sequence} could not be found!"
