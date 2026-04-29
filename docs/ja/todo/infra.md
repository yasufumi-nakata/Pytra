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

1. [x] [ID: P1-EHOST-MATRIX-S1] `gen_backend_progress.py` に emitter host マトリクス生成を追加する（`.parity-results/emitter_host_<lang>.json` から読み取り）
   - 完了: 2026-04-29。`_load_emitter_host_results()` と build/parity のアイコン化を追加した。
2. [x] [ID: P1-EHOST-MATRIX-S2] `progress-preview/backend-progress-emitter-host.md` を出力するようにする
   - 完了: 2026-04-29。`python3 tools/gen/gen_backend_progress.py` で JA/EN の `backend-progress-emitter-host.md` を生成するようにした。
3. [x] [ID: P1-EHOST-MATRIX-S3] 各 backend の P1-HOST-CPP-EMITTER タスクの S2 で `.parity-results/emitter_host_<lang>.json` に結果を書き込むよう更新する
   - 完了: 2026-04-29。各 backend TODO の S2 を emitter host 結果 JSON へ向けた。
4. [x] [ID: P1-EHOST-MATRIX-S4] JSON 形式を N×N 対応に拡張する（1ファイルに複数 hosted emitter の結果を持てるようにする）
   - 完了: 2026-04-29。`emitter_host_<host_lang>.json` の `emitters` map を正本形式として読み込むようにした。
5. [x] [ID: P1-EHOST-MATRIX-S5] `gen_backend_progress.py` を N×N マトリクス表示に対応させる（行: host 言語、列: hosted emitter）
   - 完了: 2026-04-29。`backend-progress-emitter-host.md` を host 言語 × hosted emitter の N×N 表示へ変更した。

### 保留中タスク

- P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。
