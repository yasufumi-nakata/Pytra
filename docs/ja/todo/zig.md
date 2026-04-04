<a href="../../en/todo/zig.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Zig backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-04

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

1. [x] [ID: P1-ZIG-EMITTER-S1] `src/toolchain2/emit/zig/` に Zig emitter を新規実装する — CommonRenderer + override 構成。旧 `src/toolchain/emit/zig/` と TS emitter を参考にする
   - 完了メモ (2026-04-04): `src/toolchain2/emit/zig/` に emitter 本体と CLI/runtime copier を実装し、旧 toolchain1 依存なしで toolchain2 から Zig emit できる状態にした。
2. [x] [ID: P1-ZIG-EMITTER-S2] `src/runtime/zig/mapping.json` を作成する — `calls`, `types`, `env.target`, `builtin_prefix`, `implicit_promotions` を定義
   - 完了メモ (2026-04-04): `src/runtime/zig/mapping.json` と `src/toolchain2/emit/profiles/zig.json` が揃い、toolchain2 の profile/mapping 経路で Zig target を選択可能。
3. [x] [ID: P1-ZIG-EMITTER-S3] fixture 全件の Zig emit 成功を確認する
   - 完了メモ (2026-04-04): `python3 tools/check/runtime_parity_check_fast.py --targets zig` で fixture 146 件すべて emit/compile/run まで成功。
4. [x] [ID: P1-ZIG-EMITTER-S4] Zig runtime を toolchain2 の emit 出力と整合させる
   - 完了メモ (2026-04-04): `src/runtime/zig/built_in/py_runtime.zig` と Zig runtime copier を更新し、toolchain2 emitter の union/container/callable/exception/property/super lowering と整合させた。
5. [x] [ID: P1-ZIG-EMITTER-S5] fixture の Zig run parity を通す（`zig build-exe -OReleaseFast`）
   - 完了メモ (2026-04-04): `python3 tools/check/runtime_parity_check_fast.py --targets zig` の結果が `SUMMARY cases=146 pass=146 fail=0` となり、fixture parity を完了した。
6. [x] [ID: P1-ZIG-EMITTER-S6] stdlib の Zig parity を通す（`--case-root stdlib`）
   - 完了メモ (2026-04-04): `python3 tools/check/runtime_parity_check_fast.py --targets zig --case-root stdlib` の結果が `SUMMARY cases=16 pass=16 fail=0` となり、stdlib parity を完了した。
7. [x] [ID: P1-ZIG-EMITTER-S7] sample の Zig parity を通す（`--case-root sample`）
   - 完了メモ (2026-04-04): `python3 tools/check/runtime_parity_check_fast.py --targets zig --case-root sample` の結果が `SUMMARY cases=18 pass=18 fail=0` となり、sample parity を完了した。

### P2-ZIG-LINT: emitter hardcode lint の Zig 違反を解消する

1. [x] [ID: P2-ZIG-LINT-S1] `check_emitter_hardcode_lint.py --lang zig` で全カテゴリ 0 件になることを確認する
   - 完了メモ (2026-04-04): `python3 tools/check/check_emitter_hardcode_lint.py --lang zig --verbose --no-write` の結果が `0 件の違反` となり、`module name` / `runtime symbol` / `class name` / `skip pure py` / `rt: call_cov` を解消した。
