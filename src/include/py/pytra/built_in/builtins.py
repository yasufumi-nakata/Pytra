# pytra: builtin-declarations
"""Python built-in 関数の宣言。

resolve がシグネチャを参照して型解決する。emit 対象外。
body は pass（runtime が各言語で実装）。

spec: docs/ja/spec/spec-builtin-functions.md
"""

from pytra.std import extern
from pytra.std.template import template


# ---------------------------------------------------------------------------
# §3.1 dunder 委譲型
# resolve は引数の具象型に該当の dunder があるか型チェックし、
# py_len 等のノードに変換する。
# ---------------------------------------------------------------------------

@extern
def len(x: Obj) -> int:
    return x.__len__()

@extern
def str(x: Obj) -> str:
    return x.__str__()

@extern
def bool(x: Obj) -> bool:
    return x.__bool__()

@extern
def int(x: Obj) -> int:
    return x.__int__()

@extern
def float(x: Obj) -> float:
    return x.__float__()

@extern
def repr(x: Obj) -> str:
    return x.__repr__()


# ---------------------------------------------------------------------------
# §3.2 スタンドアロン型
# 各言語の runtime が実装する関数。
# ---------------------------------------------------------------------------

@extern
def print(*args: Obj) -> None:
    pass

@extern
def isinstance(x: Obj, t: type) -> bool:
    pass

@extern
def issubclass(cls: type, parent: type) -> bool:
    pass

@extern
def round(x: float, ndigits: int = 0) -> int:
    pass

@extern
def abs(x: int) -> int:
    pass

@extern
def ord(c: str) -> int:
    pass

@extern
def chr(i: int) -> str:
    pass


# ---------------------------------------------------------------------------
# §3.3 ジェネリック型
# resolve が callsite の具象型から T を解決する。
# ---------------------------------------------------------------------------

@template("T")
@extern
def min(*args: T) -> T:
    pass

@template("T")
@extern
def max(*args: T) -> T:
    pass

@template("T")
@extern
def sorted(x: list[T]) -> list[T]:
    pass

@template("T")
@extern
def reversed(x: list[T]) -> list[T]:
    pass

@template("T")
@extern
def enumerate(x: list[T], start: int = 0) -> list[tuple[int, T]]:
    pass

@template("T", "U")
@extern
def zip(a: list[T], b: list[U]) -> list[tuple[T, U]]:
    pass


# ---------------------------------------------------------------------------
# §3.4 range（resolve で ForRange / RangeExpr に変換）
# ---------------------------------------------------------------------------

@extern
def range(stop: int) -> list[int]:
    pass

@extern
def range(start: int, stop: int) -> list[int]:
    pass

@extern
def range(start: int, stop: int, step: int) -> list[int]:
    pass
