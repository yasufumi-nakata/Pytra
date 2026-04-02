<a href="../../en/todo/zig.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Zig backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-02

## 運用ルール

- **旧 toolchain1（`src/toolchain/emit/zig/`）は変更不可。** 新規開発・修正は全て `src/toolchain2/emit/zig/` で行う（[spec-emitter-guide.md](../spec/spec-emitter-guide.md) §1）。
- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 参考資料

- 旧 toolchain1 の Zig emitter: `src/toolchain/emit/zig/`
- toolchain2 の TS emitter（参考実装）: `src/toolchain2/emit/ts/`
- 既存の Zig runtime: `src/runtime/zig/`
- emitter 実装ガイドライン: `docs/ja/spec/spec-emitter-guide.md`
- mapping.json 仕様: `docs/ja/spec/spec-runtime-mapping.md`

## 未完了タスク

### P1-ZIG-EMITTER: Zig emitter を toolchain2 に新規実装する

1. [ ] [ID: P1-ZIG-EMITTER-S1] `src/toolchain2/emit/zig/` に Zig emitter を新規実装する — CommonRenderer + override 構成。旧 `src/toolchain/emit/zig/` と TS emitter を参考にする
2. [ ] [ID: P1-ZIG-EMITTER-S2] `src/runtime/zig/mapping.json` を作成する — `calls`, `types`, `env.target`, `builtin_prefix`, `implicit_promotions` を定義
3. [ ] [ID: P1-ZIG-EMITTER-S3] fixture 全件の Zig emit 成功を確認する
4. [ ] [ID: P1-ZIG-EMITTER-S4] Zig runtime を toolchain2 の emit 出力と整合させる
5. [ ] [ID: P1-ZIG-EMITTER-S5] fixture の Zig run parity を通す（`zig build-exe -OReleaseFast`）
6. [ ] [ID: P1-ZIG-EMITTER-S6] stdlib の Zig parity を通す（`--case-root stdlib`）
7. [ ] [ID: P1-ZIG-EMITTER-S7] sample の Zig parity を通す（`--case-root sample`）

### P2-ZIG-LINT: emitter hardcode lint の Zig 違反を解消する

1. [ ] [ID: P2-ZIG-LINT-S1] `check_emitter_hardcode_lint.py --lang zig` で全カテゴリ 0 件になることを確認する
