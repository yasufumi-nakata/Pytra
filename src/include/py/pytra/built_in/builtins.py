# pytra: builtin-declarations
"""Python built-in 関数の宣言。

resolve がシグネチャを参照して型解決する。emit 対象外。
body は ... (Ellipsis) — Pylance がスタブとして認識する。

spec: docs/ja/spec/spec-builtin-functions.md
"""

from pytra.std import extern
from pytra.std.template import template
from pytra.types import Obj


# ---------------------------------------------------------------------------
# §3.1 dunder 委譲型
# resolve は引数の具象型に該当の dunder があるか型チェックし、
# py_len 等のノードに変換する。
# ---------------------------------------------------------------------------

@extern
def len(x: Obj) -> int: ...

@extern
def str(x: Obj) -> str: ...

@extern
def bool(x: Obj) -> bool: ...

@extern
def int(x: Obj) -> int: ...

@extern
def float(x: Obj) -> float: ...

@extern
def repr(x: Obj) -> str: ...


# ---------------------------------------------------------------------------
# §3.2 スタンドアロン型
# 各言語の runtime が実装する関数。
# ---------------------------------------------------------------------------

@extern
def print(*args: Obj) -> None: ...

@extern
def isinstance(x: Obj, t: type) -> bool: ...

@extern
def issubclass(cls: type, parent: type) -> bool: ...

@extern
def round(x: float, ndigits: int = 0) -> int: ...

@extern
def abs(x: int) -> int: ...

@extern
def ord(c: str) -> int: ...

@extern
def chr(i: int) -> str: ...


# ---------------------------------------------------------------------------
# §3.3 ジェネリック型
# resolve が callsite の具象型から T を解決する。
# ---------------------------------------------------------------------------

@template("T")
@extern
def min(*args: T) -> T: ...

@template("T")
@extern
def max(*args: T) -> T: ...

@template("T")
@extern
def sorted(x: list[T]) -> list[T]: ...

@template("T")
@extern
def reversed(x: list[T]) -> list[T]: ...

@template("T")
@extern
def enumerate(x: list[T], start: int = 0) -> list[tuple[int, T]]: ...

@template("T", "U")
@extern
def zip(a: list[T], b: list[U]) -> list[tuple[T, U]]: ...


# ---------------------------------------------------------------------------
# §3.4 range（resolve で ForRange / RangeExpr に変換）
# ---------------------------------------------------------------------------

@extern
def range(stop: int) -> list[int]: ...

@extern
def range(start: int, stop: int) -> list[int]: ...

@extern
def range(start: int, stop: int, step: int) -> list[int]: ...
