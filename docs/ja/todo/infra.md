<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-27

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260427.md) を参照。

## 未完了タスク

### P0-FIXTURE-PARITY-161: 全 backend を fixture 161/161 に揃える

文脈: [docs/ja/plans/p0-fixture-parity-161.md](../plans/p0-fixture-parity-161.md)

fixture が 146 → 161 に増えたが、C++ 以外の 17 backend が追いついていない。各 backend で fail しているケースを修正し 161/161 に揃える。

現状（2026-04-27 gen_backend_progress.py 出力）:

| backend | pass/total | fail |
|---|---|---|
| rs | 151/161 | 10 |
| cs | 135/161 | 26 |
| ps1 | 153/161 | 8 |
| js | 151/161 | 10 |
| ts | 150/161 | 11 |
| dart | 148/161 | 13 |
| go | 154/161 | 7 |
| java | 152/161 | 9 |
| scala | 139/161 | 22 |
| kotlin | 141/161 | 20 |
| swift | 153/161 | 8 |
| ruby | 155/161 | 6 |
| lua | 157/161 | 4 |
| php | 154/161 | 7 |
| nim | 142/161 | 19 |
| julia | 156/161 | 5 |
| zig | 150/161 | 11 |

1. [x] [ID: P0-FIX161-S1] 各 backend の fail ケースを `runtime_parity_check_fast.py --targets <lang> --case-root fixture` で特定し、fail リストを作成する
   - 2026-04-27: `backend-progress-fixture.md` の 161 件マトリクスと `.parity-results/*_fixture.json` から言語別 fail / 未実行リストを `docs/ja/plans/p0-fixture-parity-161.md` に整理。全言語 fresh sweep は重いため spot check まで実施。
2. [x] [ID: P0-FIX161-S2] fail 原因を分類する（emitter 未対応 / runtime 未実装 / golden 未生成 / EAST3 前段問題）
   - 2026-04-27: 未実行 / runtime 未実装・互換不足 / emitter 未対応 / import wiring / 型・narrowing・union runtime / 数値型 / 実行環境・profile 不整合へ分類。golden 未生成単独の blocker は現時点では確認なし。
3. [x] [ID: P0-FIX161-S3] 各 backend 担当が自分の言語を 161/161 に修正する（各言語 TODO にサブタスク展開）
   - 2026-04-27: `rust.md` / `cs.md` / `powershell.md` / `ts.md` / `dart.md` / `go.md` / `java.md` / `swift.md` / `ruby.md` / `lua.md` / `php.md` / `nim.md` / `julia.md` / `zig.md` に P0 fixture parity 161 タスクを追加。Java/Scala/Kotlin と JS/TS は共有 TODO 内で個別 ID に展開。

### 保留中タスク

- P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。
