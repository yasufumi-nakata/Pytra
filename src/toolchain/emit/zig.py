#!/usr/bin/env python3
"""Zig backend: manifest.json → Zig multi-file output.

Usage:
    python3 -m toolchain.emit.zig MANIFEST.json --output-dir emit/zig/
"""

from __future__ import annotations

import sys

from toolchain.emit.zig.emitter import transpile_to_zig_native
from toolchain.emit.loader import emit_all_modules


def _transpile_zig(east_doc: dict) -> str:
    meta = east_doc.get("meta", {})
    emit_ctx = meta.get("emit_context", {}) if isinstance(meta, dict) else {}
    is_entry = emit_ctx.get("is_entry", False) if isinstance(emit_ctx, dict) else False
    return transpile_to_zig_native(east_doc, is_submodule=not is_entry)


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.zig MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/zig"
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--output-dir" and i + 1 < len(argv):
            output_dir = argv[i + 1]
            i += 2
            continue
        if not tok.startswith("-") and input_path == "":
            input_path = tok
        i += 1

    if input_path == "":
        print("error: input manifest.json is required", file=sys.stderr)
        return 1

    return emit_all_modules(input_path, output_dir, ".zig", _transpile_zig, lang="zig")


if __name__ == "__main__":
    sys.exit(main())
