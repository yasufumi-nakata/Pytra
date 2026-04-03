<a href="../../en/todo/julia.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Julia backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-02

## 運用ルール

- **旧 toolchain1（`src/toolchain/emit/julia/`）は変更不可。** 新規開発・修正は全て `src/toolchain2/emit/julia/` で行う（[spec-emitter-guide.md](../spec/spec-emitter-guide.md) §1）。
- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 参考資料

- 旧 toolchain1 の Julia emitter: `src/toolchain/emit/julia/`
- toolchain2 の TS emitter（参考実装）: `src/toolchain2/emit/ts/`
- 既存の Julia runtime: `src/runtime/julia/`
- emitter 実装ガイドライン: `docs/ja/spec/spec-emitter-guide.md`
- mapping.json 仕様: `docs/ja/spec/spec-runtime-mapping.md`

## 未完了タスク

### P1-JULIA-EMITTER: Julia emitter を toolchain2 に新規実装する

1. [ ] [ID: P1-JULIA-EMITTER-S1] `src/toolchain2/emit/julia/` に Julia emitter を新規実装する — CommonRenderer + override 構成。旧 `src/toolchain/emit/julia/` と TS emitter を参考にする
   - 2026-04-02: toolchain2 側に Julia emitter / CLI / profile を追加し、`pytra-cli.py emit --target julia` を toolchain2 経路へ接続。現状は旧 emitter delegate の bootstrap 段階
   - 2026-04-03: bootstrap emitter に `ClosureDef -> FunctionDef` の互換変換を追加し、`test/fixture/source/py/control/nested_closure_def.py` の Julia emit failure を解消
2. [x] [ID: P1-JULIA-EMITTER-S2] `src/runtime/julia/mapping.json` を作成する — `calls`, `types`, `env.target`, `builtin_prefix`, `implicit_promotions` を定義
   - 2026-04-02: `src/runtime/julia/mapping.json` を追加し、toolchain2 Julia emitter bootstrap が参照する runtime call/type mapping を整備
3. [ ] [ID: P1-JULIA-EMITTER-S3] fixture 全件の Julia emit 成功を確認する
   - 2026-04-02: `check_py2x_transpile.py --target julia` の代表 3 件（`core/add`, `control/if_else`, `control/for_range`）で emit 成功を確認
   - 2026-04-03: `collections` 先頭群から `oop` / `signature` 前半までを順次確認し、少なくとも 90 件超で Julia emit 成功を確認
   - 2026-04-03: `oop/trait_basic.py`, `oop/trait_with_inheritance.py`, `signature/ok_fstring_format_spec.py` は Julia emitter ではなく frontend/linker 側で失敗することを確認
   - 2026-04-03: `control/exception_bare_reraise.py`, `control/exception_propagation_raise_from.py`, `control/exception_propagation_two_frames.py` は Julia emit+run parity まで復旧。`control/exception_user_defined_multi_handler.py` は Julia 1.12.5 で custom exception + multi-handler 実行時に segfault が残る
4. [ ] [ID: P1-JULIA-EMITTER-S4] Julia runtime を toolchain2 の emit 出力と整合させる
5. [ ] [ID: P1-JULIA-EMITTER-S5] fixture の Julia run parity を通す（`julia`）
   - 2026-04-03: `tools/unittest/emit/julia/test_py2julia_smoke.py` の parity 28 件が PASS（`skipped=1`）
   - 2026-04-03: `runtime_parity_check_fast.py --case-root fixture --targets julia add fib if_else for_range` で 4/4 PASS
   - 2026-04-03: exception 系 4 件のうち 3 件（`exception_bare_reraise`, `exception_propagation_raise_from`, `exception_propagation_two_frames`）が PASS。`exception_user_defined_multi_handler` は Julia runtime/class 連携の残課題
6. [ ] [ID: P1-JULIA-EMITTER-S6] stdlib の Julia parity を通す（`--case-root stdlib`）
7. [ ] [ID: P1-JULIA-EMITTER-S7] sample の Julia parity を通す（`--case-root sample`）

### P2-JULIA-LINT: emitter hardcode lint の Julia 違反を解消する

1. [x] [ID: P2-JULIA-LINT-S1] `check_emitter_hardcode_lint.py --lang julia` で全カテゴリ 0 件になることを確認する
   - 2026-04-02: `python3 tools/check/check_emitter_hardcode_lint.py --lang julia` で全カテゴリ 0 件を確認
