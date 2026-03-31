# 計画: object_container_access fixture の全言語 parity (P0-OBJECT-CONTAINER)

## 背景

既存の `typed_container_access` fixture は `dict[str, int]` / `list[str]` のような具体型コンテナのみをテストしていた。selfhost では `dict[str, object]` / `list[object]` が多用され、以下の emitter バグが露出した:

- `dict[str, object].items()` の tuple unpack → `std::get<N>` ではなく `[N]` に崩れる
- `list[object][i]` → `py_list_at_ref` ではなく bare `[]` に崩れる
- `dict[str, object].get()` → receiver が `Object<void>` のまま出る
- 既に `str` な値に `.unbox<str>()` を打つ
- `set[tuple[str, str]]` → `std::hash` 不在で compile error

これらは全て EAST3 に情報が載っている。emitter が `object` 型コンテナのケースを正しく処理できていない。

## EAST3 に載っている情報

| パターン | EAST3 のフィールド | emitter がやるべきこと |
|---|---|---|
| `dict[str, object].items()` tuple unpack | `target_plan.direct_unpack_names`, `target_type: "tuple[str,object]"`, `tuple_expanded: true` | `std::get<N>` / `.0`/`.1` で展開。value は `object` 型 |
| `list[object][i]` | `Subscript.resolved_type: "object"`, `value.resolved_type: "list[object]"` | Object list 経由の typed access。C++ なら `py_list_at_ref` |
| `dict[str, object].get()` | `resolved_type: "object"`, `yields_dynamic: true`, `semantic_tag: "stdlib.method.get"` | receiver を `Object<dict<str, object>>` として扱う |
| str 不要 unbox | `resolved_type: "str"` が代入元と代入先で一致 | 同一型なら unbox をスキップ |
| `set[tuple[str, str]]` | `resolved_type: "set[tuple[str,str]]"` | C++ は `std::hash<std::tuple<str,str>>` の特殊化が必要。Rust は `HashSet<(String, String)>` で OK |

## fixture の内容

`test/fixture/source/py/typing/object_container_access.py`:

- `test_object_dict_items_unpack()` — `dict[str, object]` の items() tuple unpack
- `test_object_list_index()` — `list[object][i]` の定数/変数インデックス
- `test_object_dict_get()` — `dict[str, object].get()` の existing / default
- `test_str_no_unnecessary_unbox()` — str passthrough / str dict get / object dict からの str 取得
- `test_set_tuple_keys()` — `set[tuple[str, str]]` の add / in / len

## 既存 fixture との関係

| fixture | コンテナ型 | 対象 |
|---|---|---|
| `typed_container_access` | `dict[str, int]`, `list[str]` | 具体型 |
| `object_container_access` | `dict[str, object]`, `list[object]` | 動的型（selfhost パターン） |

両方 PASS することで、具体型と動的型の両方をカバーできる。

## 実施

各言語の emitter で `object_container_access` fixture が compile + run parity PASS することを確認する。失敗した場合は emitter を修正する（source や EAST の変更は不要）。
