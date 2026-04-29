<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-29

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260428.md) を参照。

## 未完了タスク

### P1-EMITTER-HOST-MATRIX: emitter host マトリクスの新設と全言語 PASS

文脈: [docs/ja/plans/p1-emitter-host-matrix.md](../plans/p1-emitter-host-matrix.md)

selfhost マトリクス（full compiler）とは別に、「C++ emitter（16 モジュール）を各言語で host できるか」の emitter host マトリクスを新設する。全 18 言語で PASS を中間目標とする。

1. [ ] [ID: P1-EHOST-MATRIX-S1] `gen_backend_progress.py` に emitter host マトリクス生成を追加する（`.parity-results/emitter_host_<lang>.json` から読み取り）
2. [ ] [ID: P1-EHOST-MATRIX-S2] `progress-preview/backend-progress-emitter-host.md` を出力するようにする
3. [ ] [ID: P1-EHOST-MATRIX-S3] 各 backend の P1-HOST-CPP-EMITTER タスクの S2 で `.parity-results/emitter_host_<lang>.json` に結果を書き込むよう更新する

### 保留中タスク

- P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。
