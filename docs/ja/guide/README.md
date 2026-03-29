<a href="../../en/guide/README.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# ガイド

チュートリアルで Pytra を動かせるようになった方向けの、仕組みの解説です。仕様書ほど形式的ではなく、図やコード例を多用して「なぜそうなっているか」を説明します。

## 読む順番

1. [EAST の仕組み](./east-overview.md) — Python コードが EAST1 → EAST2 → EAST3 と変換される過程を具体例で追う
2. [emitter の仕組み](./emitter-overview.md) — EAST3 がどう C++/Go/Rust 等のコードに変換されるか、変換前後を並べて解説
3. [型システム](./type-system.md) — type_id、isinstance、ナローイング、union 型が内部でどう動くか
4. [runtime の仕組み](./runtime-overview.md) — `Object<T>`、参照カウント、コンテナの参照セマンティクスがどう動くか
5. [@extern と FFI](./extern-ffi.md) — 外部関数の呼び出し、@runtime / @extern / @template の使い方と仕組み

## このガイドの位置づけ

```
チュートリアル — まず動かす、基本を学ぶ
    ↓
ガイド（ここ）— 仕組みを理解する、設計思想を知る
    ↓
仕様書 — 正確な定義を調べる
```
