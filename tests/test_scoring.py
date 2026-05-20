from src.score_events import _to_float


def test_to_float_valid():
    assert _to_float("12.5") == 12.5


def test_to_float_invalid():
    assert _to_float("abc") == 0.0
