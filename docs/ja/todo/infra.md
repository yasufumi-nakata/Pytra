<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-30（P3-SELFHOST-PARITY 完了）

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260330.md) / [P10-REORG アーカイブ](archive/20260330-p10reorg.md) を参照。

## 未完了タスク

### P0-SELFHOST-GOLDEN-UNIFIED: selfhost golden の生成・検証スクリプトを1本に統一する

1. [ ] [ID: P0-SELFHOST-GOLDEN-S1] `tools/gen/regenerate_selfhost_golden.py` を作成する — `--target cpp,go,rs,ts` で指定した言語の selfhost golden を一括生成する。toolchain2 全 .py を emit し、`test/selfhost/<lang>/` に配置する
2. [ ] [ID: P0-SELFHOST-GOLDEN-S2] golden の回帰テストを `tools/unittest/selfhost/test_selfhost_golden.py` に統一する — 各言語の golden が最新の emit 結果と一致するか検証 + コンパイルが通るか検証。言語別の個別スクリプト（`test_cpp_selfhost_golden.py` 等）は廃止する
3. [ ] [ID: P0-SELFHOST-GOLDEN-S3] 既存の言語別 selfhost golden スクリプトを `tools/unregistered/` に退避する

（P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。）
