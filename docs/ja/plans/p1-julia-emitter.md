<a href="../../en/plans/p1-julia-emitter.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P1-JULIA-EMITTER

最終更新: 2026-04-02

## 対象

- [ID: P1-JULIA-EMITTER-S1] `src/toolchain2/emit/julia/` に Julia emitter を新規実装する
- [ID: P1-JULIA-EMITTER-S2] `src/runtime/julia/mapping.json` を作成する

## 目的

- 旧 `src/toolchain/emit/julia/` を今後の修正対象から外し、toolchain2 側に Julia backend の正本を用意する。
- emitter 実装ガイドラインに沿って、profile / mapping / emitter 入口を toolchain2 の標準構成へ揃える。

## 方針

- 第1段階では、toolchain2 側に `CommonRenderer` ベースの Julia emitter 入口を追加する。
- 既存 parity を不用意に壊さないため、bootstrap 期は旧 Julia emitter を互換 delegate として利用しつつ、新規実装の受け皿を toolchain2 側へ固定する。
- runtime 関数名・型名・target 定数は `src/runtime/julia/mapping.json` に集約する。
- 演算子や構文の基礎設定は `src/toolchain2/emit/profiles/julia.json` に置く。

## 完了条件

- `src/toolchain2/emit/julia/` が import 可能である。
- `src/runtime/julia/mapping.json` が存在し、最低限の `builtin_prefix` / `calls` / `types` / `skip_modules` / `implicit_promotions` を持つ。
- bootstrap emitter から Julia ソース文字列を生成できる。

## 決定ログ

- 2026-04-02: [ID: P1-JULIA-EMITTER-S1] Julia backend の新規実装先を `src/toolchain2/emit/julia/` に固定し、bootstrap 期は旧 emitter への delegate で移行を開始する。
- 2026-04-02: [ID: P1-JULIA-EMITTER-S2] runtime call/type の正本を `src/runtime/julia/mapping.json` に新設し、profile-driven emitter へ移行する準備を行う。
