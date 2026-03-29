<a href="../../en/spec/spec-opaque-type.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# Opaque 型仕様（extern class の型契約）

最終更新: 2026-03-29
ステータス: ドラフト

## 1. 目的

- `@extern class` で宣言された外部クラスを、Pytra の型システムで安全に扱う。
- 外部ライブラリ（SDL3 等）の handle / ポインタを rc で包まずにそのまま受け渡す。
- boxing / unboxing を発生させない。

## 2. 非目標

- opaque 型のフィールドアクセス。
- opaque 型に対する演算（算術、比較等）。
- opaque 型の継承。

## 3. 定義

`@extern class` で宣言され、本体にメソッドシグネチャのみを持つクラスは **opaque 型** として扱う。

```python
@extern
class Window:
    def set_title(self, title: str) -> None: ...
    def close(self) -> None: ...

@extern
class Renderer:
    def clear(self) -> None: ...
    def present(self) -> None: ...
```

opaque 型は以下の特徴を持つ:

- **rc で包まない**。ターゲット言語のネイティブ型（ポインタ、handle 等）としてそのまま扱う。
- **boxing しない**。`Object<void>` / `Any` にはならない。
- **名目型**。`Window` と `Renderer` は別の型であり、相互に代入できない。
- **type_id を持たない**。isinstance の対象外。
- **メソッド呼び出しは `@extern` で宣言されたもののみ**。opaque 型のメソッドは全て extern。

## 4. 型システム上の位置づけ

EAST の型カテゴリ:

| カテゴリ | rc | boxing | isinstance | 例 |
|---|---|---|---|---|
| POD | なし | なし | exact match | `int64`, `float64`, `bool`, `str` |
| クラス | あり | あり | type_id range check | ユーザー定義クラス |
| Any / object | あり | あり | — | `Any`, `object` |
| **opaque** | **なし** | **なし** | **不可** | `@extern class Window` |

`type_expr` に新しい kind を追加:

```json
{
  "kind": "OpaqueType",
  "name": "Window"
}
```

## 5. できること / できないこと

### できること

```python
@extern
class App:
    def create_window(self) -> Window: ...
    def destroy_window(self, win: Window) -> None: ...

@extern
class Window:
    def set_title(self, title: str) -> None: ...

if __name__ == "__main__":
    app: App = App()
    win: Window = app.create_window()
    win.set_title("hello")          # OK: Window の extern メソッド呼び出し
    app.destroy_window(win)          # OK: Window 型の引数に Window を渡す
```

- 同じ opaque 型を要求する引数にそのまま渡す
- `@extern` で宣言されたメソッドを呼ぶ
- 変数に代入する
- 関数の引数や戻り値として使う

### できないこと

```python
    print(win)                       # NG: str 変換不可
    x: Any = win                     # NG: Any に boxing 不可
    isinstance(win, Window)          # NG: isinstance 不可
    win.width                        # NG: フィールドアクセス不可（extern メソッドのみ）
    if win:                          # NG: truthiness 判定不可
    list_of_win: list[Window] = []   # 検討中（下記 §8）
```

## 6. 各言語への写像

| 言語 | 写像 |
|---|---|
| C++ | ポインタ（`Window*`）。rc なし。 |
| Go | ポインタ（`*Window`）または unsafe.Pointer。rc なし。 |
| Rust | `*mut Window` または `Box<Window>`。rc なし。 |
| Java | オブジェクト参照（`Window`）。GC が管理。 |
| C# | オブジェクト参照（`Window`）。GC が管理。 |
| JS/TS | そのまま（`Window`）。GC が管理。 |

GC 言語では「rc なし」は自然（GC があるから）。C++/Rust/Go では生ポインタとして扱い、ライフタイム管理は外部ライブラリの責務。

## 7. EAST 表現

### extern class 宣言

```json
{
  "kind": "ClassDef",
  "name": "Window",
  "decorators": ["extern"],
  "meta": {
    "opaque_v1": {
      "schema_version": 1
    }
  },
  "body": [
    {
      "kind": "FunctionDef",
      "name": "set_title",
      "decorators": ["extern"],
      "args": [{"name": "self"}, {"name": "title", "type": "str"}],
      "return_type": "None"
    }
  ]
}
```

### opaque 型の変数

```json
{
  "kind": "Name",
  "id": "win",
  "resolved_type": "Window",
  "type_expr": {
    "kind": "OpaqueType",
    "name": "Window"
  }
}
```

### opaque 型のメソッド呼び出し

opaque 型のメソッドは通常の `Call` + `Attribute` として表現。`@extern` メソッドとして解決済み。

## 8. 未決事項

- `list[Window]` のようにコンテナに opaque 型を入れられるか。入れる場合、list は rc だが Window は rc なし、という混在をどう扱うか。
- `Optional[Window]`（`Window | None`）は許可するか。null ポインタの表現が必要。
- opaque 型同士の等値比較（`win1 == win2`）をポインタ比較として許可するか。
- opaque 型のコンストラクタ呼び出し（`Window()` で生成）を許可するか、それとも factory メソッド経由のみか。
- `@extern class` にフィールドを持たせるケース（`width: int` 等）を opaque 型として扱うか、それとも別カテゴリか。

## 9. 関連

- [spec-type_id.md](./spec-type_id.md) — type_id 仕様（opaque 型は type_id を持たない）
- [spec-east.md](./spec-east.md) — EAST ノード仕様
- [spec-emitter-guide.md](./spec-emitter-guide.md) — emitter の写像規約
- [plans/p6-extern-method-redesign.md](../plans/p6-extern-method-redesign.md) — @runtime / @extern 再設計
