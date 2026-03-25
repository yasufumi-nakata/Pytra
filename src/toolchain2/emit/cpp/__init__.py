"""toolchain2/emit/cpp: EAST3 → C++ source emitter.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from toolchain2.emit.cpp.emitter import emit_cpp_module

__all__ = ["emit_cpp_module"]
