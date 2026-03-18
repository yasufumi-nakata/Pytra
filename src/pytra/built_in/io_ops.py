"""Extern-marked I/O helper built-ins."""


import builtins as __b

from pytra.std import extern


@extern
def py_print(value: object) -> None:
    __b.print(value)
