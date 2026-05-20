# event-meme-radar

イベント駆動型の meme radar（研究OS）です。  
v1 は **event -> meme angle -> ticker candidates -> timing/risk -> report** に集中します。

> 本リポジトリは研究用途のみ。投資助言・自動売買・ウォレット操作・秘密鍵処理は含みません。

## v1 Data Model
`data/events.csv` はトークン観測データではなく、イベント候補テーブルです。

必須列:
- event_id, event_name, date, category
- why_attention_will_gather, meme_angle, search_keywords
- ideal_accumulation_window, likely_hype_window
- too_early_risk, too_late_risk
- event_gravity_score, narrative_simplicity_score, timing_score
- why_this_may_fail, missing_data

## Outputs
- `data/ticker_candidates.csv`  
  列: event_id, ticker, ticker_type, reason, simplicity_score, ambiguity_risk
- `data/scored_events.csv`  
  preliminary_total_score = gravity + simplicity + timing（max 50）
- `reports/YYYY-MM-DD.md`  
  今日監視すべきイベントを判断するための9セクションレポート

## Scoring
- Watch Closely: 40-50
- Wait: 30-39
- Ignore: <30

## Usage
```bash
make test
make daily
```
