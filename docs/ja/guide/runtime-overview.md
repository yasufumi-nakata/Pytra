<a href="../../en/guide/runtime-overview.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# runtime の仕組み

Pytra の生成コードは、ターゲット言語のランタイムヘルパーと組み合わせて動作します。このページでは、メモリ管理、コンテナ、組み込み関数がどう動くかを解説します。

## メモリ管理: 参照カウント（RC）

Pytra は **参照カウント（Reference Counting）** でメモリを管理します。GC（ガベージコレクション）は使いません。

```
Object<Circle>
  ┌──────────────┐
  │ ptr ──────────┼──→ Circle { radius: 5.0 }
  │ rc  ──────────┼──→ ControlBlock { ref_count: 2, type_id: 1003 }
  └──────────────┘
```

- `Object<T>` は参照カウント付きのスマートポインタ
- コピーすると参照カウントが増える
- スコープを抜けると参照カウントが減る
- 参照カウントが 0 になったら解放される

Python の GC と違い、循環参照は検出しません。Pytra のコードでは循環参照を避ける設計が前提です。

## コンテナの参照セマンティクス

Python の `list` / `dict` / `set` は参照型です。関数に渡して中身を変更すると、呼び出し元にも反映されます。

```python
def add_item(xs: list[int], v: int) -> None:
    xs.append(v)

items: list[int] = [1, 2, 3]
add_item(items, 4)
print(items)  # [1, 2, 3, 4] — 変更が反映される
```

Pytra はこれを忠実に再現するため、コンテナを **参照型ラッパー** で保持します。

| 言語 | list の型 | メモリ管理 |
|---|---|---|
| C++ | `Object<list<int64>>` | RC（参照カウント）。GC がないので自前で管理 |
| Go | `*PyList[int64]` | GC。Go は GC 言語なのでポインタ共有だけで済む。RC 不要 |
| Rust | `Rc<RefCell<Vec<i64>>>` | RC + 内部可変性。GC がないので自前で管理 |
| Java/C# | `ArrayList<Long>` 等 | GC。参照型が既定 |
| Swift | `[Int64]` (class wrapper) | ARC（コンパイラが自動挿入する RC） |

### 値型への縮退

escape 解析で「この変数は関数外に出ない」と証明された場合、参照ラッパーを外して値型で保持できます。

```python
def sum_list(n: int) -> int:
    buf: list[int] = []      # buf はこの関数内でしか使われない
    i: int = 0
    while i < n:
        buf.append(i)
        i += 1
    total: int = 0
    for x in buf:
        total += x
    return total
```

linker の `container_value_locals_v1` ヒントにより、`buf` は値型（`[]int64` / `vector<int64>`）で保持されます。メモリ効率が良くなります。

## 組み込み関数

`len`, `print`, `str`, `int`, `float` 等の組み込み関数は `pytra/built_in/` に定義されています。

```python
print("hello")        # → __pytra_py_print("hello")
x = len(items)         # → __pytra_py_len(items)
s = str(42)            # → __pytra_py_to_string(42)
```

関数名の変換は `mapping.json` の `calls` マップで定義されています。emitter がハードコードすることはありません。

## 例外クラス

例外クラスは `pytra/built_in/error.py` に pure Python で定義されています。

```
PytraError
└── BaseException
    └── Exception
        ├── ValueError
        ├── RuntimeError
        ├── TypeError
        ├── IndexError
        ├── KeyError
        └── ...
```

import 不要でそのまま使えます（built_in なので）。パイプラインで全言語に自動変換されるため、言語ごとの手書き runtime は不要です。

## stdlib モジュール

Python 標準ライブラリの代替は `pytra/std/` に pure Python で実装されています。

```python
from pytra.std import math
from pytra.std import json
from pytra.std.pathlib import Path
```

これらもパイプラインで全言語に変換されます。一部の低レベル関数（ファイル I/O 等）だけが各言語のネイティブ runtime に委譲されます。

## 画像出力

PNG / GIF の書き出しは `pytra/utils/png.py` と `pytra/utils/gif.py` に pure Python で実装されています。エンコード本体（CRC32, Adler32, DEFLATE, LZW）も全て Python で書かれており、パイプラインで変換されます。

```python
from pytra.utils.png import write_rgb_png

pixels: list[int] = [0] * (256 * 256 * 3)
# ... ピクセルを書き込む ...
write_rgb_png("output.png", 256, 256, pixels)
```

## 詳しい仕様

- [ランタイム仕様](../spec/spec-runtime.md)
- [GC 仕様](../spec/spec-gc.md)
- [Boxing/Unboxing 仕様](../spec/spec-boxing.md)
- [Emitter ガイドライン §10](../spec/spec-emitter-guide.md) — コンテナ参照セマンティクス
