import csv
from datetime import UTC, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EVENTS_CSV = BASE_DIR / "data" / "events.csv"
OUTPUT_CSV = BASE_DIR / "data" / "ticker_candidates.csv"
DECISION_LOG_CSV = BASE_DIR / "data" / "decision_log.csv"

TYPE_ORDER = ["direct", "derivative", "person", "location", "slang", "controversy", "meme_phrase"]


def _log(event_id: str, stage: str, status: str, reason: str) -> None:
    with DECISION_LOG_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now(UTC).isoformat(), event_id, stage, status, reason])


def _sanitize(text: str) -> str:
    return "".join(ch for ch in text.upper() if ch.isalnum())


def generate_candidate_rows(event: dict) -> list[dict]:
    event_id = event["event_id"]
    name = event["event_name"]
    words = [w for w in name.replace(":", " ").replace("-", " ").split() if w]

    direct = _sanitize("".join(words[:2]))[:6]
    derivative = _sanitize(words[0] + "X")[:6] if words else ""
    location = "USA" if "US " in name or "Super Bowl" in name else ""
    meme_phrase = _sanitize((event.get("meme_angle") or "").split("+")[0])[:6]

    candidates = [
        ("direct", direct, "Event name compression", 9, "low"),
        ("derivative", derivative, "Variant of primary event ticker", 7, "medium"),
        ("person", "", "Needs confirmed person anchor", 5, "high"),
        ("location", location, "Location-based shorthand", 6, "medium"),
        ("slang", "WAGMI", "Common crypto slang mapping", 4, "high"),
        ("controversy", "", "Requires controversy trigger", 3, "high"),
        ("meme_phrase", meme_phrase, "Meme-angle phrase compression", 8, "medium"),
    ]

    rows = []
    for ticker_type, ticker, reason, simplicity, risk in candidates:
        if ticker:
            rows.append(
                {
                    "event_id": event_id,
                    "ticker": ticker[:10],
                    "ticker_type": ticker_type,
                    "reason": reason,
                    "simplicity_score": simplicity,
                    "ambiguity_risk": risk,
                }
            )
            _log(event_id, "ticker_generation", "ok", f"{ticker_type}:{ticker}")
        else:
            _log(event_id, "ticker_generation", "skipped", f"{ticker_type}:insufficient context")
    return rows


def run() -> None:
    all_rows = []
    with EVENTS_CSV.open("r", newline="", encoding="utf-8") as f:
        for event in csv.DictReader(f):
            all_rows.extend(generate_candidate_rows(event))

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["event_id", "ticker", "ticker_type", "reason", "simplicity_score", "ambiguity_risk"],
        )
        writer.writeheader()
        writer.writerows(all_rows)


if __name__ == "__main__":
    run()
