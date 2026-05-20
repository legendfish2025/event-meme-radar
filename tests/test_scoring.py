from src.score_events import _priority, _to_int


def test_to_int_valid_and_invalid():
    assert _to_int("12") == 12
    assert _to_int("x") == 0


def test_priority_ranges():
    assert _priority(45) == "Watch Closely"
    assert _priority(35) == "Wait"
    assert _priority(20) == "Ignore"
