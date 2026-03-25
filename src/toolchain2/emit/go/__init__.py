"""toolchain2/emit/go: EAST3 → Go source emitter.

お手本 emitter: 他言語 emitter のテンプレートとなる設計。

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from toolchain2.emit.go.emitter import emit_go_module

__all__ = ["emit_go_module"]
