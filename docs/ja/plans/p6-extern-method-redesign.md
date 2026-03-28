<a href="../../en/plans/p6-extern-method-redesign.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P6-EXTERN-METHOD-REDESIGN: @extern_method / @abi の再設計

最終更新: 2026-03-29
ステータス: 案

## 背景

現在 `containers.py` 等の built_in 宣言は `@extern_method` + `@abi` の2デコレータを使うが:

- `@extern_method` の引数が冗長（module, symbol, tag の3つ）
- `@abi` は未使用（実装もテストもない）
- module / symbol / tag に重複情報がある

## 結論

### 2つのデコレータに整理

| デコレータ | 対象 | 意味 |
|---|---|---|
| `@extern` | opaque 型 | 外部で定義された不透明型。rc なし、boxing なし。handle として扱う |
| `@runtime("namespace")` | runtime 実装クラス | Pytra の型システムに組み込まれたクラス。rc あり。runtime に実装がある |

### `@runtime` によるクラス宣言

```python
@runtime("pytra.core")
class list(Generic[T]):
    def append(self, x: T) -> None: ...
    def extend(self, x: list[T]) -> None: ...
    def pop(self, index: int = -1) -> T: ...
    def sort(self) -> None: ...
    def clear(self) -> None: ...

@runtime("pytra.core")
class dict(Generic[K, V]):
    def get(self, key: K) -> V: ...
    def items(self) -> list[tuple[K, V]]: ...
```

- `@runtime("pytra.core")` でクラスが属する namespace を宣言
- メソッドに個別のデコレータは不要（`@runtime` クラス内のメソッドは全て runtime 実装）
- `@namespace` は不要（`@runtime` の引数に含まれる）
- `@method` は不要（`@runtime` クラス内のメソッドは暗黙的に全て extern）

### `@extern` による opaque 型宣言

```python
@extern
class Window:
    def set_title(self, title: str) -> None: ...
    def close(self) -> None: ...

@extern
class App:
    def create_window(self) -> Window: ...
    def destroy_window(self, win: Window) -> None: ...
```

- rc で包まない（spec-opaque-type.md 参照）
- メソッドは全て外部実装

### 自動導出ルール

`@runtime("pytra.core")` の `class list` の `extend` メソッドの場合:

- module: `pytra.core.list`（namespace + class名）
- symbol: `list.extend`（class名 + メソッド名）
- tag: `stdlib.method.extend`（自動導出）
- runtime 関数名: mapping.json で変換（`list.extend` → `py_list_extend_mut` 等）

### `@abi` 廃止

`@abi` は廃止する。理由:

- 未実装・未使用なので影響ゼロ
- arg mode（`ref` / `ref_readonly` / `value` / `value_readonly`）は全て不要と判断

### arg mode が不要な理由

- 全引数は rc のまま渡す（`ref` のみ）
- `ref_readonly` は escape 解析に役立たない（関数に渡した時点で追跡不能）
- `value` / `value_readonly` は外部 FFI 用に検討したが、runtime ラッパーが deref すれば済む
- エイリアス問題（`a.extend(a)`）により rc を剥がすと dangling reference になる

### runtime ヘルパーの引数は全て rc 前提

runtime ヘルパーは全て rc 付き（`Object<list<T>>` / `*PyList[T]`）を引数に取る。1パターンだけ実装すればよい。

### `@extern` と `@runtime` の違い

| | `@extern` | `@runtime` |
|---|---|---|
| 用途 | 外部ライブラリ（SDL3 等） | Pytra built_in / std |
| rc | なし（opaque handle） | あり（Pytra の型システム） |
| boxing | なし | あり |
| type_id | なし | あり |
| isinstance | 不可 | 可 |
| 型カテゴリ | OpaqueType | 通常のクラス |

## 現状との比較

| | 現状 | 新設計 |
|---|---|---|
| list.append | `@extern_method(module="pytra.core.list", symbol="list.append", tag="stdlib.method.append")` | `@runtime` クラス内に `def append(...)` を書くだけ |
| list.extend | 上記 + `@abi(args={"x": "value"})` | 同上（arg mode 不要） |
| Window | `@extern class Window` | `@extern class Window`（変更なし） |

## サブタスク

1. [ID: P6-REDESIGN-S1] `@runtime` デコレータを parser に実装し、自動導出ルールを組み込む
2. [ID: P6-REDESIGN-S2] `containers.py` を `@runtime` 記法に書き換える
3. [ID: P6-REDESIGN-S3] `@extern_method` を廃止する（parser からの受理を停止）
4. [ID: P6-REDESIGN-S4] `@abi` を廃止する
5. [ID: P6-REDESIGN-S5] spec-east.md の `meta.runtime_abi_v1` を廃止する
6. [ID: P6-REDESIGN-S6] チュートリアル・ガイドの `@abi` 言及を削除する
7. [ID: P6-REDESIGN-S7] emitter guide を更新し、`@runtime` クラスのメソッドの runtime 実装ルールを記載する

## 未決事項

- `@extern` の関数版（`@extern def native_sqrt(x: float) -> float: ...`）はそのまま残すか
- `@runtime` で関数（メソッドでなく）を宣言するケースがあるか
- 既存の `containers.py` の書き換え量の見積もり

## 決定ログ

- 2026-03-28: 案A〜D を検討。案D（`@namespace` + `@method` 最小記述、自動導出）を推奨とした。
- 2026-03-28: arg mode（ref / ref_readonly / value / value_readonly）の4種類を検討。
- 2026-03-28: エイリアス問題（`a.extend(a)`）を発見。rc を剥がせないことを確認。
- 2026-03-29: `ref_readonly` は escape 解析に役立たないと判断。arg mode は全て不要と結論。
- 2026-03-29: 外部 FFI でも runtime ラッパーが deref すればよく、`value` / `value_readonly` も不要と判断。
- 2026-03-29: `@abi` 廃止、arg mode 廃止に決定。
- 2026-03-29: `@method` は `@extern` と区別がつかない問題が発覚。`@runtime("namespace")` と `@extern` の2つに整理。`@namespace` も `@method` も不要に。
