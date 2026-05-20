import csv
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SCORED_CSV = BASE_DIR / "data" / "scored_events.csv"
REPORT_DIR = BASE_DIR / "reports"


def _load_rows() -> list[dict]:
    with SCORED_CSV.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run() -> None:
    today = date.today().isoformat()
    rows = _load_rows()
    top = rows[:5]

    lines = [f"# Daily Event Meme Radar ({today})", "", "研究用途のみ。投資助言ではありません。", ""]

    lines += ["## 1. Top Priority Today", ""]
    watch = [r for r in rows if r["priority_class"] == "Watch Closely"]
    for r in watch[:3]:
        lines.append(f"- {r['event_name']} ({r['date']}) score={r['preliminary_total_score']} | {r['likely_hype_window']}")
    if not watch:
        lines.append("- No Watch Closely events today.")

    lines += ["", "## 2. Top Events Ranked", "", "| rank | event | date | score | priority |", "|---:|---|---|---:|---|"]
    for i, r in enumerate(top, start=1):
        lines.append(f"| {i} | {r['event_name']} | {r['date']} | {r['preliminary_total_score']} | {r['priority_class']} |")

    lines += ["", "## 3. Ticker Candidates by Event", ""]
    for r in top:
        lines.append(f"- **{r['event_name']}**: {r['ticker_candidates']}")

    lines += ["", "## 4. Immediate Search Queries", ""]
    for r in top:
        lines.append(f"- {r['search_keywords']}")

    lines += ["", "## 5. Watch Closely / Wait / Ignore", ""]
    for cls in ["Watch Closely", "Wait", "Ignore"]:
        names = [r["event_name"] for r in rows if r["priority_class"] == cls]
        lines.append(f"- {cls}: {', '.join(names) if names else 'None'}")

    lines += ["", "## 6. Invalidation Checklist", "", "- Event date delay/cancellation", "- Narrative fragmentation", "- Missing catalyst data unresolved"]

    lines += ["", "## 7. Danger Flags", ""]
    for r in rows:
        if r["danger_flags"]:
            lines.append(f"- {r['event_name']}: {r['danger_flags']}")

    lines += ["", "## 8. Missing Data", ""]
    for r in rows:
        if r["missing_data"]:
            lines.append(f"- {r['event_name']}: {r['missing_data']}")

    lines += ["", "## 9. Research Notes", "", "- Preliminary scores are deterministic sum of gravity+simplicity+timing (max 50).", "- Use this report to decide what to monitor today; no buy/sell recommendation is included."]

    out = REPORT_DIR / f"{today}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated: {out}")


if __name__ == "__main__":
    run()
