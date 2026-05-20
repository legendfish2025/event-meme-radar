import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EVENTS_CSV = BASE_DIR / "data" / "events.csv"
TICKERS_CSV = BASE_DIR / "data" / "ticker_candidates.csv"
OUTPUT_CSV = BASE_DIR / "data" / "scored_events.csv"


def _to_int(v: str) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _priority(total: int) -> str:
    if 40 <= total <= 50:
        return "Watch Closely"
    if 30 <= total <= 39:
        return "Wait"
    return "Ignore"


def run() -> None:
    ticker_map: dict[str, list[str]] = {}
    with TICKERS_CSV.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ticker_map.setdefault(row["event_id"], []).append(f"{row['ticker']}({row['ticker_type']})")

    out = []
    with EVENTS_CSV.open("r", newline="", encoding="utf-8") as f:
        for e in csv.DictReader(f):
            gravity = _to_int(e["event_gravity_score"])
            simplicity = _to_int(e["narrative_simplicity_score"])
            timing = _to_int(e["timing_score"])
            total = gravity + simplicity + timing
            missing_data = e.get("missing_data", "").strip()
            danger_flags = []
            if _to_int(e["timing_score"]) <= 4:
                danger_flags.append("timing_weak")
            if "delay" in (e.get("why_this_may_fail", "").lower()):
                danger_flags.append("delay_risk")
            if missing_data:
                danger_flags.append("missing_data")

            out.append(
                {
                    "event_id": e["event_id"],
                    "event_name": e["event_name"],
                    "category": e["category"],
                    "date": e["date"],
                    "event_gravity_score": gravity,
                    "narrative_simplicity_score": simplicity,
                    "timing_score": timing,
                    "preliminary_total_score": total,
                    "priority_class": _priority(total),
                    "ticker_candidates": " | ".join(ticker_map.get(e["event_id"], [])),
                    "search_keywords": e["search_keywords"],
                    "likely_hype_window": e["likely_hype_window"],
                    "too_early_late_risk": f"early:{e['too_early_risk']} / late:{e['too_late_risk']}",
                    "danger_flags": "|".join(danger_flags),
                    "missing_data": missing_data,
                    "why_this_may_fail": e["why_this_may_fail"],
                }
            )

    out.sort(key=lambda x: x["preliminary_total_score"], reverse=True)

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "event_id","event_name","category","date","event_gravity_score","narrative_simplicity_score",
                "timing_score","preliminary_total_score","priority_class","ticker_candidates","search_keywords",
                "likely_hype_window","too_early_late_risk","danger_flags","missing_data","why_this_may_fail",
            ],
        )
        writer.writeheader()
        writer.writerows(out)


if __name__ == "__main__":
    run()
