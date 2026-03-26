# pytra: builtin-declarations
"""pytra.std.pathlib: Path クラスの宣言（v2 extern）。"""

from pytra.std import extern_class, extern_method, extern_fn


@extern_fn(module="pytra.std.pathlib", symbol="Path", tag="stdlib.fn.Path")
def Path(s: str) -> Path: ...


@extern_class(module="pytra.std.pathlib", symbol="Path", tag="stdlib.class.Path")
class Path:
    @extern_method(module="pytra.std.pathlib", symbol="pathlib.write_text", tag="stdlib.method.write_text")
    def write_text(self, content: str) -> None: ...

    @extern_method(module="pytra.std.pathlib", symbol="pathlib.write_bytes", tag="stdlib.method.write_bytes")
    def write_bytes(self, data: bytes) -> None: ...

    @extern_method(module="pytra.std.pathlib", symbol="pathlib.read_text", tag="stdlib.method.read_text")
    def read_text(self) -> str: ...
