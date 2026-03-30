# 計画: 整数リテラルの冗長キャスト除去 (P0-CPP-LITERAL-CAST)

## 背景

C++ emitter の `_emit_constant`（`emitter.py:1026-1027`）が、整数リテラルを常に型キャスト付きで出力している:

```cpp
// 現状: 冗長
for (int64 i = int64(0); i < max_iter; i += 1) {
int64 x = int64(42);
int32 count = int32(0);

// 理想: 安全な場合はキャストなし
for (int64 i = 0; i < max_iter; i += 1) {
int64 x = 42;
int32 count = 0;
```

この問題は C++ 固有ではない。Go / Rust / Java 等でも「この型×この値範囲ならリテラルそのまま、それ以外はラップ」という同じ構造がある。各言語の emitter が独自に実装するのではなく、CommonRenderer で共通化すべき。

## 各言語のリテラル型規則

| 言語 | リテラルの型決定 | キャスト不要な条件 |
|---|---|---|
| C++ | 値に応じて `int` → `long` → `long long` | `int32`/`int64` で `int` 範囲内 |
| Go | 整数リテラルは untyped constant | ほぼ全てキャスト不要（型推論が効く） |
| Rust | 整数リテラルはサフィックスなしだと推論 | 文脈から型推論できればキャスト不要 |
| Java | `int` がデフォルト、`L` サフィックスで `long` | `int` で `int` 範囲内なら不要、`long` は `L` が要る |
| C# | Java と同様 | 同上 |

## 設計: CommonRenderer に `literal_nowrap_ranges` を追加

### profile (mapping.json or profile.json) に設定を追加

```json
{
  "literal_nowrap_ranges": {
    "int32": [-2147483648, 2147483647],
    "int64": [-2147483648, 2147483647],
    "float64": "always"
  }
}
```

- キー: EAST の `resolved_type`
- 値: `[min, max]` — リテラル値がこの範囲内ならキャスト不要。`"always"` なら常にキャスト不要。
- テーブルに載っていない型はキャスト必須（現状維持）。

### CommonRenderer の `render_constant` を拡張

```python
def render_constant(self, node: dict[str, JsonVal]) -> str:
    value = node.get("value")
    if value is None:
        return self._none_literal()
    if isinstance(value, bool):
        return self._bool_literal(value)
    if isinstance(value, str):
        return self._quote_string(value)
    if isinstance(value, int):
        rt = self._str(node, "resolved_type")
        if self._literal_needs_wrap(rt, value):
            return self._wrap_int_literal(rt, value)
        return str(value)
    return str(value)
```

- `_literal_needs_wrap(rt, value)`: `literal_nowrap_ranges` テーブルを参照し、ラップが必要か判定
- `_wrap_int_literal(rt, value)`: 型名でラップ。デフォルトは `type_name(value)`。言語固有の形式が必要な場合は override 可能（例: Java の `(long)42` や `42L`）

### C++ emitter の `_emit_constant` から整数キャストロジックを除去

CommonRenderer が判定するため、C++ emitter の override は不要になる。`_emit_constant` の整数分岐は CommonRenderer に委譲する形に縮退する。

## 判定ルール（C++ の場合）

`literal_nowrap_ranges` テーブル:

| EAST 型 | 範囲 | 理由 |
|---|---|---|
| `int32` | [-2^31, 2^31-1] | `int` → `int32_t` は同幅変換 |
| `int64` | [-2^31, 2^31-1] | `int` → `int64_t` は安全な拡大変換 |
| `float64` | always | `double` リテラルはそのまま |
| `int8`, `int16` | (なし) | narrowing — 常にキャスト必要 |
| `uint*` | (なし) | 符号変換のリスク — 常にキャスト必要 |

## 影響範囲

- 生成コードの見た目が変わる（`int64(0)` → `0`）ため、golden の差分が出る
- **実行結果は変わらない** — 各言語の暗黙変換規則に従った等価な変換
- fixture + sample の parity check で回帰がないことを確認する

## 実施順序

1. CommonRenderer に `literal_nowrap_ranges` テーブル読み込み + `render_constant` 拡張を実装
2. C++ の profile/mapping に `literal_nowrap_ranges` を設定
3. C++ emitter の `_emit_constant` から整数キャストロジックを CommonRenderer へ委譲
4. fixture + sample parity 確認
5. 他言語（Go, Rust 等）にも `literal_nowrap_ranges` を設定（別タスク可）

## 対象外

- `ForRange` 等で直接ハードコードされている `int64(0)` / `int64(1)`（2445行目等）も同様に修正すべきだが、別タスクでもよい
