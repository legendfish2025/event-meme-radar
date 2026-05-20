from src.generate_tickers import generate_candidate_rows


def test_generate_candidate_rows_has_required_types():
    event = {
        "event_id": "E999",
        "event_name": "OpenAI DevDay 2026",
        "meme_angle": "AI agent meme formats + productivity satire",
    }
    rows = generate_candidate_rows(event)
    types = {r["ticker_type"] for r in rows}
    assert "direct" in types
    assert "derivative" in types
    assert "meme_phrase" in types


def test_generate_candidate_rows_schema_keys():
    event = {
        "event_id": "E998",
        "event_name": "NBA Finals 2026",
        "meme_angle": "star player legacy meme wars",
    }
    row = generate_candidate_rows(event)[0]
    assert set(row.keys()) == {
        "event_id",
        "ticker",
        "ticker_type",
        "reason",
        "simplicity_score",
        "ambiguity_risk",
    }
