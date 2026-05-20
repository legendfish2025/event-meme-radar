# event-meme-radar

Solana / Pump.fun 系ミームコイン向けの**イベント駆動リサーチOS**です。

> 本リポジトリは調査・研究用途のみです。投資助言、自動売買、ウォレット操作、秘密鍵処理は含みません。

## Features
- イベントデータを重み付きでスコアリング
- ticker 候補の自動生成（品質チェック付き）
- 危険信号（risk flags）と missing data の検知
- 失敗理由を decision log に保存
- 日次Markdownレポート生成 (`make daily`)

## Structure
- `config/`: スコア重み・リスクルール・ウォッチリスト
- `data/`: 入力/中間データ（CSV）
- `src/`: コアロジック
- `reports/`: 日次レポート
- `tests/`: 単体テスト

## Usage
```bash
make test
make daily
```

`make daily` 実行後に `reports/YYYY-MM-DD.md` が生成されます。
