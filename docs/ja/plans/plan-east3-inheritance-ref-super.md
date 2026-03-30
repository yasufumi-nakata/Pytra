# 計画: EAST3 継承クラスの ref 一貫性 + super() 解決 (P0-EAST3-INHERIT)

## 背景

`inheritance_virtual_dispatch_multilang` fixture で Rust emitter が `Rc<RefCell<LoudDog>>` と `Box<dyn AnimalMethods>` の衝突を起こしている。原因は EAST3 の lowering にある。

### 問題 1: 継承階層の基底クラスが `class_storage_hint: "value"` になる

EAST3 の現状:

| クラス | base | class_storage_hint |
|---|---|---|
| `Animal` | (なし) | `"value"` |
| `Dog` | `Animal` | `"ref"` |
| `LoudDog` | `Dog` | `"ref"` |

`Dog` が `Animal` を継承して `ref` になるなら、`Animal` も `ref` でなければ型の一貫性がない。`a: Animal = LoudDog()` で value/ref のセマンティクスが衝突する。

C++ では vtable ポインタを持つ型は value にできない（スライシング問題）。Go は interface で暗黙 ref。Rust は `Box<dyn Trait>` で ref。いずれの言語でも、継承階層に参加する基底クラスは参照セマンティクスが必要。

### 問題 2: `super()` が未解決のまま EAST3 に残る

`LoudDog.speak` 内の `super().speak()`:

- `super()` の `resolved_type` が `"unknown"`
- `super().speak()` の `resolved_type` も `"unknown"`
- emitter は戻り値型を知れず、`Box<dyn Any>` に崩れる

`super()` は静的に解決可能: `LoudDog` の `super()` は `Dog`、`Dog.speak()` の戻り値は `str`。EAST3 でこれを確定すべき。

## 設計

### 問題 1 の修正

EAST3 lowering（`class_storage_hint` 決定ロジック）で、**派生クラスが存在する基底クラスも `ref` に昇格**する:

1. クラス定義を全て収集
2. 継承関係を走査し、1つでも派生クラスがある基底クラスを `ref` に昇格
3. 推移的に適用（A ← B ← C なら A も B も `ref`）

これにより継承階層全体が `ref` で統一され、emitter は `Rc<RefCell<T>>` / `shared_ptr<T>` / interface で一貫して扱える。

### 問題 2 の修正

EAST3 lowering（または EAST2 resolve）で、`super()` を解決する:

1. `Call(Name("super"))` を検出
2. 現在のクラスの `base` を参照し、super の型を確定
3. `super().method()` の `Attribute` ノードに receiver type = base class を設定
4. method の戻り値型を base class のメソッド定義から解決

EAST3 の `super()` Call ノードに以下を追加:
- `resolved_type`: base class 名（例: `"Dog"`）
- チェーンされた method call の `resolved_type`: method の戻り値型

## 影響範囲

- 継承を使う全 fixture に影響する可能性がある
- C++ は既に vtable ベースで動いているので `ref` 昇格は自然
- Go は interface 経由なので影響なし
- Rust は `Box<dyn Trait>` / `Rc` の統一が可能になる
- fixture + sample parity の全言語確認が必要

## 実施順序

1. EAST3 lowering で継承基底クラスの `class_storage_hint` を `ref` に昇格する
2. EAST3 lowering（または EAST2 resolve）で `super()` の型を解決する
3. 全言語の fixture parity に回帰がないことを確認する
4. Rust emitter の `inheritance_virtual_dispatch_multilang` が compile + run parity PASS することを確認する
