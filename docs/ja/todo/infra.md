<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-11

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260403.md) を参照。

## 未完了タスク

### P0-SELFHOST-MODULE-CLOSURE: selfhost build の transitive import 解決漏れを修正する

selfhost build driver が `ImportFrom` の transitive closure を完全に拾えておらず、emit 対象 module セットから依存先が漏れるケースがある。

**発端**: 2026-04-11、C++ selfhost build で `expand_defaults.h` が `#include "toolchain/resolve/py/type_norm.h"` を出すが、`type_norm` が emit 対象から抜けていて g++ で missing include に落ちる。

**判断**: これは EAST / backend / emitter のいずれでもなく、selfhost build driver（どの `.py` を emit 対象にするか決める上位レイヤー）の問題。C++ backend で補完すると、他言語 selfhost で責務がずれて再発明される。全 selfhost で共通の build driver 側で直す。

**影響**: C++ selfhost が S5 で停止中。他言語 selfhost（Rust / Go / Nim / Lua / TS / Swift / Zig 等）にも波及する可能性がある（Go では偶然カバーされていただけの可能性）。

1. [ ] [ID: P0-SELFHOST-CLOSURE-S1] selfhost build driver の module collection ロジックを調査し、transitive import 解決漏れの原因を特定する
2. [ ] [ID: P0-SELFHOST-CLOSURE-S2] entry point からの reachability closure が `ImportFrom` を確実に追うように修正する
3. [ ] [ID: P0-SELFHOST-CLOSURE-S3] C++ selfhost で `expand_defaults.py → type_norm.py` が emit 対象に入ることを確認する
4. [ ] [ID: P0-SELFHOST-CLOSURE-S4] Go selfhost の既存テストに回帰がないことを確認する（module set が広がるため）

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
