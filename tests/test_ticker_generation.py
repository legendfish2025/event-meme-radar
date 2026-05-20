from src.generate_tickers import generate_ticker


def test_generate_ticker_basic():
    assert generate_ticker("Pepe Bonk") == "PEPEBO"


def test_generate_ticker_alnum_only():
    assert generate_ticker("$c@t!!") == "CT"
