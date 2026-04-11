<a href="../../en/todo/go.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Go backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-10

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 未完了タスク

### P7-GO-SELFHOST-RUNTIME: Go selfhost バイナリを実際に動かして parity PASS する

文脈: [docs/ja/plans/p7-go-selfhost-runtime.md](../plans/p7-go-selfhost-runtime.md)

P6 で go build は通ったが、selfhost バイナリが実際に fixture/sample/stdlib を変換して parity PASS するにはまだギャップがある。

1. [ ] [ID: P7-GO-SELFHOST-RT-S1] linker の type_id 割り当てで外部ベースクラス（CommonRenderer(ABC) 等）の階層解決を修正する — object にフォールバックする
2. [ ] [ID: P7-GO-SELFHOST-RT-S2] Go emitter 自身の Go 翻訳を selfhost golden に含める — 循環依存除外の見直し。`emit/go/` を golden に含められるようにする
3. [ ] [ID: P7-GO-SELFHOST-RT-S3] CLI wrapper（`main.go`）を追加する — EAST3 JSON を読んで Go コードを emit する最小エントリポイント
4. [ ] [ID: P7-GO-SELFHOST-RT-S4] `python3 tools/run/run_selfhost_parity.py --selfhost-lang go` を実行し、fixture + sample + stdlib の parity PASS を確認する
