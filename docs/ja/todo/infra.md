<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-30（P3-SAMPLE-AUTO-COPY 完了）

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260330.md) / [P10-REORG アーカイブ](archive/20260330-p10reorg.md) を参照。

## 未完了タスク

### P3-SELFHOST-PARITY: selfhost 済みコンパイラによる fixture/sample parity 検証

文脈: [docs/ja/plans/p3-selfhost-parity.md](../plans/p3-selfhost-parity.md)

注: 各言語の selfhost ビルドが通るかは言語次第。スクリプトの骨格は先に作り、ビルドが通る言語から順に検証する。ビルドが通らない言語は `selfhost_<lang>.json` に `build: fail` が記録される。

1. [ ] [ID: P3-SELFHOST-PARITY-S1] `tools/run/run_selfhost_parity.py` を作成する — selfhost バイナリのビルド → emit → compile + run → stdout 比較の一連のフローを実行する
2. [ ] [ID: P3-SELFHOST-PARITY-S2] 結果を `.parity-results/selfhost_<lang>.json` に記録する — `gen_backend_progress.py` が読み取り selfhost マトリクスに反映
3. [ ] [ID: P3-SELFHOST-PARITY-S3] Python 行のハードコードを廃止し、`.parity-results/selfhost_python.json` から読む形に移行する
4. [ ] [ID: P3-SELFHOST-PARITY-S4] selfhost マトリクスの PASS 条件を「fixture + sample の全件 parity PASS」に確定する

### P20-INT32: int のデフォルトサイズを int64 → int32 に変更

文脈: [docs/ja/plans/p4-int32-default.md](../plans/p4-int32-default.md)

前提: Go selfhost 完了後に着手。影響範囲が大きいため P4 → P20 に降格。

1. [ ] [ID: P20-INT32-S1] spec-east.md / spec-east2.md の `int` → `int32` 正規化ルール変更
2. [ ] [ID: P20-INT32-S2] resolve の型正規化を修正
3. [ ] [ID: P20-INT32-S3] sample 18 件のオーバーフロー確認 + 必要な箇所を `int64` に明示
4. [ ] [ID: P20-INT32-S4] golden 再生成 + 全 emitter parity 確認
