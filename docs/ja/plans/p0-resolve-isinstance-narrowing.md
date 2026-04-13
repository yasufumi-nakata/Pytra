# P0-RESOLVE-ISINSTANCE-NARROWING: union 型に対する isinstance narrowing を修正する

最終更新: 2026-04-13

## 背景

C++ selfhost build で `isinstance(value, dict)` 後の narrowing が bare `dict`（パラメータなし）になり、emitter が `dict` と `dict[str, JsonVal]` を別の型と誤判定して不正な covariant copy を生成する。

## 問題

`value` の型が `JsonVal`（= `None | bool | int | float | str | list[JsonVal] | dict[str, JsonVal]`）のとき:

```python
if isinstance(value, dict):
    call_args.append(value)  # ← ここで value の型は？
```

現状の resolve: `value` → `dict`（bare、パラメータなし）

正しい narrowing: `value` → `dict[str, JsonVal]`

理由: union `JsonVal` の構成要素で `dict` にマッチするのは `dict[str, JsonVal]` の 1 つだけ。isinstance は runtime でジェネリクスパラメータを検査できないが、**型推論としては union の構成要素からパラメータ付き型を特定できる**。

## 影響範囲

- resolve の isinstance narrowing は全言語の EAST3 に影響する
- `isinstance(x, list)` で `list[int]` に narrowing される等、dict 以外にも適用される
- Python の typing の制約（isinstance にパラメータ付き型を渡せない）を resolve の型推論で補完する形

## 修正方針

resolve が `isinstance(value, T)` を処理するとき:

1. `value` の `resolved_type` が union 型であれば、構成要素から `T` のサブタイプをフィルタする
2. マッチが 1 つなら、そのパラメータ付き型を narrowing 結果にする
3. マッチが複数なら、それらの union を narrowing 結果にする（例: `dict[str, int] | dict[str, str]` → `isinstance(x, dict)` → `dict[str, int] | dict[str, str]`）
4. マッチが 0 なら、既存動作（bare 型）を維持

## 例

```python
x: int | str | None = ...
if isinstance(x, int):
    # x → int（union の構成要素から int を取り出す）

y: list[int] | dict[str, float] | None = ...
if isinstance(y, dict):
    # y → dict[str, float]（dict にマッチする構成要素は 1 つ）

z: JsonVal = ...
if isinstance(z, dict):
    # z → dict[str, JsonVal]（JsonVal の union 内で dict は dict[str, JsonVal] のみ）
```

## fixture

検証用 fixture `test/fixture/source/py/typing/isinstance_union_narrowing.py` は追加済み。
