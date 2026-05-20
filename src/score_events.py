import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
EVENTS_CSV = BASE_DIR / "data" / "events.csv"
TICKERS_CSV = BASE_DIR / "data" / "ticker_candidates.csv"
OUTPUT_CSV = BASE_DIR / "data" / "scored_events.csv"
DECISION_LOG_CSV = BASE_DIR / "data" / "decision_log.csv"
WEIGHTS_YAML = BASE_DIR / "config" / "scoring_weights.yaml"
RISK_YAML = BASE_DIR / "config" / "risk_rules.yaml"


def _log(event_id: str, stage: str, status: str, reason: str) -> None:
    with DECISION_LOG_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([datetime.utcnow().isoformat(), event_id, stage, status, reason])


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _load_weights(path: Path) -> dict:
    weights = {}
    in_weights = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.strip() == "weights:":
            in_weights = True
            continue
        if in_weights and not line.startswith("  "):
            break
        if in_weights and ":" in line:
            k, v = line.strip().split(":", 1)
            weights[k.strip()] = float(v.strip())
    return weights


def _load_required_fields(path: Path) -> list:
    required = []
    in_required = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.strip() == "required_fields:":
            in_required = True
            continue
        if in_required:
            s = line.strip()
            if not s:
                continue
            if s.startswith("-"):
                required.append(s[1:].strip())
            elif not line.startswith("  "):
                break
    return required


def run() -> None:
    weights = _load_weights(WEIGHTS_YAML)
    required_fields = _load_required_fields(RISK_YAML)

    ticker_map = {}
    with TICKERS_CSV.open("r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ticker_map[row["source_event_id"]] = row

    out_rows = []
    with EVENTS_CSV.open("r", newline="", encoding="utf-8") as f:
        for event in csv.DictReader(f):
            event_id = event.get("id", "")
            missing = [k for k in required_fields if not (event.get(k) or "").strip()]

            score = 0.0
            score += _to_float(event.get("social_mention_growth")) * weights["social_mention_growth"]
            score += _to_float(event.get("volume_spike")) * weights["volume_spike"]
            score += _to_float(event.get("dev_activity")) * weights["dev_activity"]
            score += _to_float(event.get("launch_proximity")) * weights["launch_proximity"]
            score += _to_float(event.get("influencer_signal")) * weights["influencer_signal"]

            risks = []
            if _to_float(event.get("liquidity_usd")) < 10000:
                risks.append("low_liquidity")
            if _to_float(event.get("top_holder_pct")) > 20:
                risks.append("concentration_risk")
            if (event.get("name_contains_suspicious") or "").lower() == "true":
                risks.append("suspicious_name")

            ticker_row = ticker_map.get(event_id, {})
            ticker = ticker_row.get("ticker", "")
            ticker_status = ticker_row.get("status", "missing")

            failure_reasons = []
            if missing:
                failure_reasons.append("missing data: " + ",".join(missing))
            if ticker_status != "ok":
                failure_reasons.append("ticker issue")
            if risks:
                _log(event_id, "risk_scan", "flagged", "|".join(risks))

            out_rows.append(
                {
                    "id": event_id,
                    "token_name": event.get("token_name", ""),
                    "ticker": ticker,
                    "score": round(score, 2),
                    "risk_flags": "|".join(risks),
                    "missing_data": "|".join(missing),
                    "failure_reasons": "|".join(failure_reasons),
                }
            )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "token_name",
                "ticker",
                "score",
                "risk_flags",
                "missing_data",
                "failure_reasons",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    run()
