"""Pure-Python source-of-truth for predicate helpers."""

from pytra.std import template


@template("T")
def py_any(values: T) -> bool:
    for value in values:
        if bool(value):
            return True
    return False


@template("T")
def py_all(values: T) -> bool:
    for value in values:
        if not bool(value):
            return False
    return True
