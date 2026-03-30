<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-30（P0-SELFHOST-GOLDEN-UNIFIED S1-S2 完了）

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260330.md) / [P10-REORG アーカイブ](archive/20260330-p10reorg.md) を参照。

## 未完了タスク

### P0-SELFHOST-MATRIX-AUTO-REFRESH: parity check 末尾で selfhost マトリクスを自動再集約する

1. [ ] [ID: P0-SELFHOST-REFRESH-S1] parity check（fast 版）の末尾に `_maybe_refresh_selfhost_python()` を追加する — `selfhost_python.json` の mtime が 30 分以上古ければ `run_selfhost_parity.py --selfhost-lang python` を自動実行して `.parity-results/selfhost_python.json` を再集約する
2. [ ] [ID: P0-SELFHOST-REFRESH-S2] 再集約後に `gen_backend_progress.py` が selfhost マトリクスに反映することを確認する（既存の `_maybe_regenerate_progress` の 10 分ルールで自動実行される）

（P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。）
