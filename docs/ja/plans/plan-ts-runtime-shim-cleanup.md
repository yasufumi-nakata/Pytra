# 計画: TS/JS runtime の Python ビルトイン shim を廃止する (P0-TS-SHIM-CLEANUP)

## 背景

`src/runtime/ts/built_in/py_runtime.ts` に Python ビルトイン名の shim が大量に export されている:

```typescript
export const int = Number;         // Python int() の shim
export type int = number;
export function match(...) { ... } // Python re.match の shim
```

生成コードが `import { int, match, ... } from "./pytra_built_in_py_runtime"` でこれらを import し、Python と同じ名前で呼び出している。

## 問題

1. **`int` は JavaScript の予約語ではないが混乱を招く**: `Number` のエイリアスにする意味がない
2. **`match` は `re.match` の機能**: `pytra_built_in_py_runtime` ではなく `pytra_std_re` から来るべき
3. **emitter が Python のビルトイン名をそのまま emit している**: EAST3 の `runtime_call` / `semantic_tag` / `mapping.json` を使って言語固有の名前に変換すべき
4. **import 文が肥大化する**: 1行に大量の名前が並ぶ

## あるべき姿

| Python | 現状の TS 出力 | あるべき TS 出力 |
|---|---|---|
| `int(x)` | `int(x)` (shim 経由) | `Math.trunc(Number(x))` or `Number(x)` |
| `str(x)` | `pyStr(x)` (既に直接) | そのまま |
| `len(x)` | `pyLen(x)` (既に直接) | そのまま |
| `re.match(p, s)` | `match(p, s)` (shim 経由) | `pyReMatch(p, s)` or mapping.json 解決 |
| `perf_counter()` | `perf_counter()` (shim 経由) | mapping.json で解決 |

`pyStr`, `pyLen` のように `py` prefix 付きで直接 runtime 関数を呼ぶパターンは正しい。`int`, `match` のように Python 名をそのまま使うパターンが問題。

## 修正方針

1. emitter が EAST3 の `runtime_call` / `semantic_tag` を見て、mapping.json の `calls` テーブルで TS 固有の関数名に解決する
2. runtime の shim export (`int`, `match` 等) を削除する
3. mapping.json の `calls` テーブルに不足があれば追加する

## 対象の shim (要調査)

`py_runtime.ts` から export されている Python ビルトイン名の一覧を調査し、mapping.json で解決すべきものと runtime に残すべきものを分類する。

## 影響範囲

- 生成コードの import 文が変わる
- runtime の export が減る
- fixture + sample + stdlib の TS/JS parity 確認が必要
