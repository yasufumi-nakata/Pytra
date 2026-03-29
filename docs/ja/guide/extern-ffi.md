<a href="../../en/guide/extern-ffi.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# @extern と FFI

Pytra のコードから、各ターゲット言語のネイティブ関数やライブラリを呼び出す仕組みを解説します。

## @extern とは

`@extern` は「この関数はターゲット言語側で実装されている」と宣言するデコレータです。Pytra 側にはシグネチャ（引数と戻り値の型）だけを書き、中身は書きません。

```python
@extern
def native_sqrt(x: float) -> float: ...

if __name__ == "__main__":
    print(native_sqrt(2.0))
```

emitter はこの宣言を見て、ターゲット言語側の `native_sqrt` を呼び出すコードを生成します。

## 使い方の例: SDL3 バインディング

外部ライブラリを使いたい場合:

```python
@extern
def sdl_init(flags: int) -> int: ...

@extern
def sdl_create_window(title: str, w: int, h: int, flags: int) -> int: ...

@extern
def sdl_destroy_window(window: int) -> None: ...

if __name__ == "__main__":
    sdl_init(0)
    win = sdl_create_window("Hello", 800, 600, 0)
    # ... 使う ...
    sdl_destroy_window(win)
```

ターゲット言語側で `sdl_init`, `sdl_create_window`, `sdl_destroy_window` を C の SDL3 API にバインドする実装を用意します。

## @runtime — runtime 実装クラス

`@runtime("namespace")` は、Pytra runtime 側に実装があるクラスを宣言します。主に built-in / std の宣言に使います。

```python
from pytra.std import runtime

@runtime("pytra.core")
class list:
    def append(self, x: int) -> None: ...
    def pop(self, index: int = -1) -> int: ...
```

class 自体の namespace だけを書けば、各メソッドの `module` / `symbol` / `tag` は parser が自動導出します。

## @template — ジェネリック関数

`@template` は型パラメータを持つ関数を定義します。

```python
from pytra.std import template

@template("T")
def identity(x: T) -> T:
    return x

if __name__ == "__main__":
    print(identity(42))        # T = int
    print(identity("hello"))   # T = str
```

C++ ではテンプレート、Rust ではジェネリクス、Go では型パラメータに変換されます。

## extern クラス

クラス全体を extern にすることもできます:

```python
@extern
class NativeWindow:
    width: int
    height: int

    def resize(self, w: int, h: int) -> None: ...
    def close(self) -> None: ...
```

ターゲット言語側で `NativeWindow` クラスの実装を用意します。Pytra 側はインターフェース（シグネチャ）だけを知っています。

method ごとに個別 symbol を指定したい場合は、class 内の method に `@extern(module=..., symbol=..., tag=...)` を付けます。

## extern の仕組み

1. parser が `@extern` を EAST1 に保持する
2. resolve が extern 関数のシグネチャを型環境に登録する（中身がなくても型は確定する）
3. EAST3 では `decorators: ["extern"]` として保持される
4. emitter は extern 関数を **委譲コード**（ネイティブ関数への薄いラッパー）として生成する
5. ユーザーがターゲット言語側に実装を用意する

emitter が生成するのはシグネチャに基づく委譲コードだけであり、実装本体は生成しません。

## runtime 側の extern

`pytra/std/*` のモジュール（math, time, pathlib 等）の一部関数は内部的に `@extern` で実装されています。例えば `perf_counter()` は:

1. `pytra/std/time.py` に `@extern def perf_counter() -> float: ...` と宣言
2. 各言語の runtime に `perf_counter` のネイティブ実装がある
3. emitter が `mapping.json` に従って名前を写像する

ユーザーが `from pytra.std.time import perf_counter` と書くと、この仕組みが裏で動きます。

## 詳しい仕様

- [利用仕様](../spec/spec-user.md) — @extern の入力制約
- [Emitter ガイドライン §4](../spec/spec-emitter-guide.md) — @extern 委譲コード生成
