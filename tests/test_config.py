from leaguepedia_sb_parser.grid_parser import GridParser
from leaguepedia_sb_parser.qq_parser import QQParser
from leaguepedia_sb_parser.live_parser import LiveParser
from mwrogue.esports_client import EsportsClient
from leaguepedia_sb_parser.components.errors import GameNotFound

live_sample_ids = ["VN2_489795204"]
grid_sample_ids = ["LOLTMNT03_115957", "LOLTMNT03_115928"]
grid_invalid_id = "invalid_id"
qq_sample_ids = ["9347", "9348", "10787", "10891"]
site = EsportsClient("lol")


def test_grid():
    for grid_id in grid_sample_ids:
        output = GridParser(site, "Season 1 World Championship").parse_series([grid_id], header=True)
        assert isinstance(output[1], list)
        assert isinstance(output[0], str)

    exception_raised = False
    try:
        GridParser(site, "Season 1 World Championship").parse_series(grid_invalid_id, header=True)
    except GameNotFound:
        exception_raised = True

    assert exception_raised


def test_live():
    for live_id in live_sample_ids:
        output = LiveParser(site=site, event="Season 1 World Championship").parse_series([live_id], header=True)
        assert isinstance(output[1], list)
        assert isinstance(output[0], str)


def test_qq():
    for qq_id in qq_sample_ids:
        output = QQParser(site, "Season 1 World Championship").parse_series(qq_id, include_header=False)
        assert isinstance(output[0], str)
        assert isinstance(output[1], list)
