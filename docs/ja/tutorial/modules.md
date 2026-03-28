<a href="../../en/tutorial/modules.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 使えるモジュール

Pytra では Python 標準ライブラリの代わりに `pytra.std.*` を使います。このページでは、よく使うモジュールを実例付きで紹介します。

## math — 数学関数

```python
from pytra.std import math

x: float = math.sqrt(2.0)
y: float = math.sin(math.pi / 4.0)
z: float = math.floor(3.7)    # 3.0
```

使える関数: `sqrt`, `sin`, `cos`, `tan`, `exp`, `log`, `log10`, `fabs`, `floor`, `ceil`, `pow`

定数: `math.pi`, `math.e`

## pathlib — ファイルパス操作

```python
from pytra.std.pathlib import Path

p: Path = Path("data/output")
p.mkdir(parents=True, exist_ok=True)

text: str = Path("input.txt").read_text()
Path("output.txt").write_text("hello")

name: str = Path("image.png").stem      # "image"
ext: str = Path("image.png").suffix     # ".png"
```

## json — JSON の読み書き

```python
from pytra.std import json

data: str = json.dumps({"name": "pytra", "version": 1})
# → '{"name": "pytra", "version": 1}'

obj = json.loads('{"x": 42}')
```

## time — 時間計測

```python
from pytra.std.time import perf_counter

start: float = perf_counter()
# ... 処理 ...
elapsed: float = perf_counter() - start
print("elapsed: " + str(elapsed) + " sec")
```

## sys — コマンドライン引数

```python
from pytra.std import sys

for arg in sys.argv:
    print(arg)
```

## os — ファイルシステム操作

```python
from pytra.std import os

cwd: str = os.getcwd()
os.makedirs("output/images", exist_ok=True)
full: str = os.path.join("data", "file.txt")
```

## random — 乱数

```python
from pytra.std import random

random.seed(42)
x: float = random.random()          # 0.0 〜 1.0
n: int = random.randint(1, 100)     # 1 〜 100
```

## 画像出力 — PNG / GIF

Pytra にはトランスパイル可能な画像書き出しヘルパーが付属しています。

```python
from pytra.utils.png import write_rgb_png
from pytra.utils.gif import save_gif

# 幅 256 x 高さ 256 の RGB 画像を書き出す
pixels: list[int] = [0] * (256 * 256 * 3)
# ... pixels に色を書き込む ...
write_rgb_png("output.png", 256, 256, pixels)
```

サンプルの多くがこのヘルパーを使って PNG/GIF を生成しています。

## 全モジュール一覧

上記以外にも `argparse`, `glob`, `re`, `enum`, `timeit` 等が使えます。
全モジュール・全関数の一覧は [pylib モジュール一覧（仕様書）](../spec/spec-pylib-modules.md) を参照してください。
