import csv
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SCORED_CSV = BASE_DIR / "data" / "scored_events.csv"
REPORT_DIR = BASE_DIR / "reports"


def run() -> None:
    today = date.today().isoformat()
    out_path = REPORT_DIR / f"{today}.md"

    rows = []
    with SCORED_CSV.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    lines = [
        f"# Daily Event Meme Radar ({today})",
        "",
        "研究用途レポート（投資助言ではありません）。",
        "",
        "## Event Scores",
        "",
        "| id | token | ticker | score | risk_flags | missing_data | failure_reasons |",
        "|---|---|---|---:|---|---|---|",
    ]

    for r in rows:
        lines.append(
            "| {id} | {token_name} | {ticker} | {score} | {risk_flags} | {missing_data} | {failure_reasons} |".format(
                **r
            )
        )

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated: {out_path}")


if __name__ == "__main__":
    run()
