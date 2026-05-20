import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EVENTS_CSV = BASE_DIR / "data" / "events.csv"
OUTPUT_CSV = BASE_DIR / "data" / "ticker_candidates.csv"
DECISION_LOG_CSV = BASE_DIR / "data" / "decision_log.csv"


def _log(event_id: str, stage: str, status: str, reason: str) -> None:
    with DECISION_LOG_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([datetime.utcnow().isoformat(), event_id, stage, status, reason])


def generate_ticker(name: str) -> str:
    clean = "".join(ch for ch in name.upper() if ch.isalnum())
    return clean[:6]


def run() -> None:
    rows = []
    with EVENTS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for event in reader:
            event_id = event.get("id", "")
            token_name = (event.get("token_name") or "").strip()

            if not token_name:
                rows.append(
                    {
                        "source_event_id": event_id,
                        "ticker": "",
                        "status": "failed",
                        "reason": "missing token_name",
                    }
                )
                _log(event_id, "ticker_generation", "failed", "missing token_name")
                continue

            ticker = generate_ticker(token_name)
            if len(ticker) < 3:
                rows.append(
                    {
                        "source_event_id": event_id,
                        "ticker": ticker,
                        "status": "failed",
                        "reason": "ticker too short",
                    }
                )
                _log(event_id, "ticker_generation", "failed", "ticker too short")
                continue

            rows.append(
                {
                    "source_event_id": event_id,
                    "ticker": ticker,
                    "status": "ok",
                    "reason": "generated",
                }
            )
            _log(event_id, "ticker_generation", "ok", "generated")

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["source_event_id", "ticker", "status", "reason"]
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    run()
