<a href="../../en/todo/nim.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Nim backend

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

## 参考資料

- Nim emitter: `src/toolchain/emit/nim/`
- TS emitter（参考実装）: `src/toolchain/emit/ts/`
- Nim runtime: `src/runtime/nim/`
- emitter 実装ガイドライン: `docs/ja/spec/spec-emitter-guide.md`
- mapping.json 仕様: `docs/ja/spec/spec-runtime-mapping.md`

## 未完了タスク

### P20-NIM-SELFHOST: Nim emitter で toolchain2 を Nim に変換し実行できるようにする

1. [ ] [ID: P20-NIM-SELFHOST-S0] selfhost 対象コードの型注釈補完（他言語と共通）
2. [ ] [ID: P20-NIM-SELFHOST-S1] toolchain2 全 .py を Nim に emit し、compile + 実行できることを確認する
3. [ ] [ID: P20-NIM-SELFHOST-S2] selfhost 用 Nim golden を配置する
4. [ ] [ID: P20-NIM-SELFHOST-S3] `run_selfhost_parity.py --selfhost-lang nim --emit-target nim --case-root fixture` で fixture parity PASS
5. [ ] [ID: P20-NIM-SELFHOST-S4] `run_selfhost_parity.py --selfhost-lang nim --emit-target nim --case-root sample` で sample parity PASS
