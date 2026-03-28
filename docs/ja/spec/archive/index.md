<a href="../../../en/spec/archive/index.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 仕様アーカイブ（index）

`docs/ja/spec/archive/` は、`docs/ja/spec/` から退役した旧仕様を保管する場所です。  
`docs/ja/spec/` 直下は常に現行仕様のみを置きます。

## 運用ルール

- 旧仕様へ移すときは、ファイル名を `YYYYMMDD-<slug>.md` 形式にします。
- 先頭に次の3点を明記します。
  - 元ファイル
  - 退役理由
  - 現行の参照先
- アーカイブ追加時は、この `index.md` にリンクを追記します。

## アーカイブ一覧

- 2026-03-28（toolchain1 その他の旧仕様）:
  - [20260328-spec-abi.md](./20260328-spec-abi.md) — @extern/@abi C++ 固有 ABI 型
  - [20260328-spec-any-prohibition.md](./20260328-spec-any-prohibition.md) — Any 禁止ガイド
  - [20260328-spec-gsk-native-backend.md](./20260328-spec-gsk-native-backend.md) — Go/Swift/Kotlin 個別 backend 契約
  - [20260328-spec-ruby-native-backend.md](./20260328-spec-ruby-native-backend.md) — Ruby 個別 backend 契約
  - [20260328-spec-options.md](./20260328-spec-options.md) — 旧オプション仕様
  - [20260328-spec-make.md](./20260328-spec-make.md) — Makefile 生成仕様
- 2026-03-28（toolchain1 C++ 固有仕様 → toolchain2 では EAST3 Optimizer / CommonRenderer / spec-emitter-guide §10 に統合）:
  - [20260328-spec-cpp-optimizer.md](./20260328-spec-cpp-optimizer.md)
  - [20260328-spec-cpp-list-reference-semantics.md](./20260328-spec-cpp-list-reference-semantics.md)
- 2026-03-28（toolchain1 言語別 backend 契約 → toolchain2 では spec-emitter-guide.md + profiles に統合）:
  - [20260328-spec-java-native-backend.md](./20260328-spec-java-native-backend.md)
  - [20260328-spec-lua-native-backend.md](./20260328-spec-lua-native-backend.md)
  - [20260328-spec-zig-native-backend.md](./20260328-spec-zig-native-backend.md)
- 2026-02-24:
  - [20260224-spec-east123.md](./20260224-spec-east123.md)
  - [20260224-spec-east123-migration.md](./20260224-spec-east123-migration.md)
  - [20260224-spec-east1-build.md](./20260224-spec-east1-build.md)
