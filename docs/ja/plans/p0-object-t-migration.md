# P0: Object\<T\> 移行 — ControlBlock + テンプレート view 方式への移行

最終更新: 2026-03-21

関連 TODO:
- `docs/ja/todo/index.md` の `ID: P0-OBJECT-T-MIGRATION-*`

## 背景

現行の `object` 型は `{pytra_type_id tag; rc<RcObject> _rc;}` の型消去済み単一型で、以下の問題を抱えている:

1. `dict<K,V>` や `list<T>` を `object` に格納するのに `rc_new` ラップが必要（emitter が複雑化）
2. `py_types.h` の forward declaration 時点で `RcObject` のサブクラスか判定できず、テンプレート SFINAE が失敗する（include 順序問題）
3. upcast/downcast に `static_cast` を直接使い、型安全性がない
4. `RcObject` を継承する全型が仮想デストラクタ + 仮想 `py_type_id()` を持つ必要があり、オーバーヘッドが大きい

新設計 `Object<T>` は `ControlBlock`（実体管理）+ テンプレート view 方式で、これらの問題を根本的に解決する。仕様は `docs/ja/spec/spec-object.md` を参照。

## 影響範囲

| カテゴリ | ファイル数 | 概要 |
|---|---|---|
| runtime core headers | ~17 | `py_types.h`, `gc.h`, `list.h`, `dict.h`, `tagged_value.h` 等 |
| runtime .cpp | ~6 | `gc.cpp`, `io.cpp` 等 |
| emitter (C++ コード生成) | ~15 | `cpp_emitter.py`, `type_bridge.py`, `call.py`, `stmt.py` 等 |
| tests | ~10 | `test_py2cpp_features.py`, `test_cpp_runtime_*` 等 |

## 移行戦略

### フェーズ 1: ControlBlock + Object\<T\> の導入（runtime 並行運用）

現行の `RcObject` / `rc<T>` / `object` を残したまま、新 `ControlBlock` / `Object<T>` を `core/object.h` に追加する。両方の型が共存する状態。

- **1-1**: `core/object.h` に `ControlBlock`, `Object<T>`, `make_object<T>`, `upcast<To>` を実装
- **1-2**: `core/object.h` に `is_subtype` 区間判定を実装（既存の `type_id_support.h` と並行）
- **1-3**: `TypeInfo` 型テーブルと `g_type_table` を実装（リンカーの type_id 割り当てと統合）

### フェーズ 2: emitter の移行（Object\<T\> 形式の C++ を生成）

emitter が生成する C++ コードを `Object<T>` 形式に順次移行する。

- **2-1**: emitter のクラス定義 emit を `Object<T>` 対応に変更（`class_def.py`）
- **2-2**: emitter の変数宣言 emit を `Object<T>` 対応に変更（`stmt.py`）
- **2-3**: emitter の代入・upcast emit を `Object<T>` の view 変換に変更
- **2-4**: emitter の isinstance/downcast emit を `is_subtype` + `static_cast` に変更
- **2-5**: emitter の関数引数・戻り値の型 emit を `Object<T>` 対応に変更（`type_bridge.py`）
- **2-6**: emitter の Any/object 型 emit を `Object<void>` または型消去版 `Object<>` に変更

### フェーズ 3: list\<T\> / dict\<K,V\> の Object 統合

`list<T>` と `dict<K,V>` を `Object<T>` でラップ可能にする。

- **3-1**: `list<T>` から `RcObject` 継承を除去し、`Object<list<T>>` で管理する形に移行
- **3-2**: `dict<K,V>` から `RcObject` 継承を除去し、`Object<dict<K,V>>` で管理する形に移行
- **3-3**: emitter の list/dict boxing を `Object<list<T>>` / `Object<dict<K,V>>` に変更

### フェーズ 4: 旧型の撤去

旧 `RcObject` / `rc<T>` / `object` を全て除去する。

- **4-1**: `RcObject` クラスを削除（全参照を `ControlBlock` に移行済み）
- **4-2**: `rc<T>` テンプレートを削除（全参照を `Object<T>` に移行済み）
- **4-3**: 旧 `object` 型を削除（`Object<void>` または新 `object` typedef に統一）
- **4-4**: `tagged_value.h` を削除（ControlBlock に統合済み）
- **4-5**: `gc.h` を `ControlBlock` ベースの rc 管理に書き換え

### フェーズ 5: テスト・検証

- **5-1**: `test_py2cpp_features.py` の全コンパイル + 実行テストが通る
- **5-2**: `test_cpp_runtime_type_id.py` の type_id テストが通る
- **5-3**: selfhost multi-module transpile が動作する
- **5-4**: sample/py の全 18 ケースが C++ で compile + run できる

## 非対象

- 非 C++ backend への影響（C++ runtime のみの変更）
- GC アルゴリズムの変更（rc ベースを維持、ControlBlock に移行するのみ）
- Python 側コード（`src/pytra/`）への変更

## リスク

- フェーズ 1〜3 の並行運用期間に、旧型と新型の混在で emitter が複雑化する可能性
- `list<T>` / `dict<K,V>` の `RcObject` 継承除去は、runtime ヘッダーの大規模書き換えを伴う
- selfhost が依存する runtime ヘッダーも同時に更新が必要

## 決定ログ

- 2026-03-21: 現行 `object` の include 順序問題（forward declaration + SFINAE 失敗）が P0-17 の根本原因であることを特定。`Object<T>` + `ControlBlock` 方式への移行を計画。
