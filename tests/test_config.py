from leaguepedia_sb_parser.bayes_parser import BayesParser
from leaguepedia_sb_parser.qq_parser import QQParser
from leaguepedia_sb_parser.live_parser import LiveParser
from mwrogue.esports_client import EsportsClient

live_sample_ids = ["KR_6273834781", "KR_6273812725", "KR_6261074461"]
bayes_sample_ids = ["ESPORTSTMNT02_3130849", "ESPORTSTMNT04_2270140"]
qq_sample_ids = ["9347", "9348", "10787", "10891"]
site = EsportsClient("lol")


def test_bayes():
    for bayes_id in bayes_sample_ids:
        output = BayesParser(site, "Season 1 World Championship").parse_series([bayes_id], header=True)
        assert isinstance(output[1], list)
        assert isinstance(output[0], str)


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
