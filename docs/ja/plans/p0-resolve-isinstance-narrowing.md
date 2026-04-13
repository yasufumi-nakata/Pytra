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

- `test/fixture/source/py/typing/isinstance_union_narrowing.py` — 単一 isinstance での union narrowing（追加済み）
- `test/fixture/source/py/typing/isinstance_chain_narrowing.py` — if/elif/else チェーンでの段階的 union narrowing（追加済み）。C++/Go/Rust/Zig で FAIL。else ブランチで残り型への narrowing が効いていない。

## 段階的 narrowing（elif/else チェーン）

### 問題

```python
y: str | int = ...
if isinstance(y, str):
    # y → str（これは動く）
else:
    # y → int であるべき（str が排除された残り）
    remainder: int = y % 3  # ← C++/Go/Rust/Zig で FAIL
```

4 メンバの union でも同様:

```python
x: int | str | list[int] | None = ...
if isinstance(x, int):
    # x → int
elif isinstance(x, str):
    # x → str（int が排除された残り union から str を選択）
elif isinstance(x, list):
    # x → list[int]（int, str が排除された残り union から list を選択）
else:
    # x → None（int, str, list[int] が排除された残り）
```

### 原因

P0-RESOLVE-NARROW-S1 の修正は `if isinstance(x, T):` の正ブランチ（T にマッチする構成要素をパラメータ付きで取り出す）だけを対象にしている。`else` / `elif` で「マッチしなかった残りの構成要素」に narrowing する処理が欠けている。

### 修正方針

resolve が `isinstance(x, T)` を処理するとき:

1. **正ブランチ（if/elif の中）**: union の構成要素から T にマッチするものを取り出す（既に実装済み）
2. **偽ブランチ（else / elif の続き）**: union の構成要素から T にマッチするものを**除外**し、残りの union を `resolved_type` にする
   - 残りが 1 つなら、その型に narrowing（例: `str | int` の `str` 排除 → `int`）
   - 残りが 2 つ以上なら、残りの union を構成（例: `int | str | list[int] | None` の `int` 排除 → `str | list[int] | None`）
   - 残りが 0 なら、到達不能（dead code）

3. `elif isinstance(x, T2):` は、前の分岐で除外された残り union に対して同じ処理を繰り返す

### not isinstance パターン

```python
if not isinstance(x, dict):
    return  # x は dict 以外の union 構成要素
# ここでは x → dict[str, JsonVal]（既に動く）
```

これは既に compile 側の guard propagation で処理されている。追加修正は不要。
