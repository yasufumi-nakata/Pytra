<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-03

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260403.md) を参照。

## 未完了タスク

### P0-MAPPING-FQCN-KEY: mapping.json の calls キーを完全修飾に統一する

文脈: [docs/ja/plans/p0-mapping-fqcn-key.md](../plans/p0-mapping-fqcn-key.md)

共通基盤 `code_emitter.py` の `resolve_runtime_symbol_name` が `runtime_symbol`（bare `"sin"` 等）だけで mapping.json を引いている。ユーザー定義関数と衝突するリスクあり。EAST3 は `runtime_module_id` + `runtime_symbol` を完全修飾で持っているので、mapping.json キーも `"pytra.std.math.sin"` のように完全修飾にする。

1. [ ] [ID: P0-FQCN-KEY-S1] `resolve_runtime_symbol_name` に `module_id` パラメータを追加し完全修飾で先に引く
2. [ ] [ID: P0-FQCN-KEY-S2] 全言語の mapping.json キーを完全修飾に統一、重複エントリ削除
3. [ ] [ID: P0-FQCN-KEY-S3] bare fallback を削除
4. [ ] [ID: P0-FQCN-KEY-S4] `check_runtime_call_coverage.py` の突き合わせを完全修飾に対応
5. [ ] [ID: P0-FQCN-KEY-S5] C++ parity で代表確認（各言語は各担当に委譲）

### P10-LEGACY-TOOLCHAIN-REMOVAL: 旧 toolchain + pytra-cli.py を削除する

文脈: [docs/ja/plans/p10-legacy-toolchain-removal.md](../plans/p10-legacy-toolchain-removal.md)

**開始はユーザーの合図待ち。** 全担当が停止しているタイミングで実行する。

削除対象:
- `src/toolchain/`（旧 emitter、旧 compile、旧 frontends、旧 misc）
- `src/pytra-cli.py`（旧 CLI。`src/pytra-cli2.py` が正本）
- 旧パイプラインを参照している test/spec/docs の記述

1. [ ] [ID: P10-LEGACY-RM-S1] `src/toolchain/` を削除する
2. [ ] [ID: P10-LEGACY-RM-S2] `src/pytra-cli.py` を削除し、`src/pytra-cli2.py` を `src/pytra-cli.py` にリネームする
3. [ ] [ID: P10-LEGACY-RM-S3] spec / tutorial / README の旧パイプライン参照を更新する
4. [ ] [ID: P10-LEGACY-RM-S4] `run_local_ci.py` 等のツールから旧パイプライン参照を削除する

### P20-DATA-DRIVEN-TESTS: パイプライン系テストのデータ駆動化

文脈: [docs/ja/plans/plan-emit-expect-data-driven-tests.md](../plans/plan-emit-expect-data-driven-tests.md)

ステータス: **保留中** — 既存テストが他 agent により変更中のため、安定してから Phase 1 に着手する。

`tools/unittest/` の 267 スクリプトのうち ~80件はパイプライン系（入力→parse/resolve/lower/emit→期待出力）で、JSON データで定義できる。残り ~190件（tooling/selfhost/link 等）は Python テストとして残す。

**Phase 1: emit 層で方式を確立**

1. [ ] [ID: P20-DDT-S1] `test/cases/emit/cpp/` に JSON テストケース 5〜10 件を作成する
2. [ ] [ID: P20-DDT-S2] `tools/unittest/test_emit_cases.py` を実装する（pytest parametrize で JSON 走査）
3. [ ] [ID: P20-DDT-S3] `test_common_renderer.py` の対応テストを JSON に移行し、元メソッドを削除する

**Phase 2: パイプライン層に横展開**

4. [ ] [ID: P20-DDT-S4] `test/cases/{east1,east2,east3}/` に JSON テストケースを作成する
5. [ ] [ID: P20-DDT-S5] `tools/unittest/test_pipeline_cases.py` を実装する
6. [ ] [ID: P20-DDT-S6] `tools/unittest/ir/` と `tools/unittest/toolchain2/` の対応テストを段階的に JSON に移行する

**Phase 3: smoke テストの統合**

7. [ ] [ID: P20-DDT-S7] `tools/unittest/emit/<lang>/test_py2*_smoke.py` (~20件) を JSON に移行する
8. [ ] [ID: P20-DDT-S8] `tools/unittest/common/test_pylib_*.py` (~10件) を JSON に移行する
9. [ ] [ID: P20-DDT-S9] 空になったスクリプトを削除する

### 保留中タスク

- P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。
