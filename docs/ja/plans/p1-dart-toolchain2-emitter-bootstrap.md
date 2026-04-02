<a href="../../en/plans/p1-dart-toolchain2-emitter-bootstrap.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P1: Dart toolchain2 emitter bootstrap

## 対象

- [ID: P1-DART-EMITTER-S1] `src/toolchain2/emit/dart/` に toolchain2 用の Dart emitter 入口を追加する
- [ID: P1-DART-EMITTER-S2] `src/runtime/dart/mapping.json` を追加する

## 方針

1. `toolchain2` 側に Dart emitter の正式な入口を追加する。
2. EAST3 lowering 用 profile と runtime mapping を追加し、`target_language="dart"` を有効化する。
3. parity で必要な multi-file 出力と runtime コピーを `tools/check/runtime_parity_check_fast.py` に接続する。
4. 既存 Dart native emitter の出力をまず再利用し、toolchain2 側の配線を先に成立させる。

## 非対象

- Dart emitter 本体の hardcode 解消
- CommonRenderer ベースへの全面移行
- fixture/sample 全件 parity 通過

## 受け入れ基準

1. `lower_east2_to_east3(..., target_language="dart")` が profile 不在で落ちない。
2. `toolchain2.emit.dart.emitter.emit_dart_module()` で linked EAST3 を Dart へ変換できる。
3. parity ツールが Dart の emit ディレクトリ構造と runtime コピーを扱える。

## 決定ログ

- 2026-04-02: 旧 Dart native emitter の生成品質を維持しつつ、toolchain2 側の入口と検証導線を先に立ち上げる方針を採用。
