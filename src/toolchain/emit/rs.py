#!/usr/bin/env python3
"""RS backend: manifest.json → RS multi-file output."""

from __future__ import annotations
import sys

from toolchain.emit.rs.emitter.rs_emitter import transpile_to_rust
from toolchain.emit.loader import emit_all_modules


def _transpile_rs(east_doc: dict) -> str:
    meta = east_doc.get("meta", {})
    emit_ctx = meta.get("emit_context", {}) if isinstance(meta, dict) else {}
    module_id = emit_ctx.get("module_id", "") if isinstance(emit_ctx, dict) else ""
    # built_in modules are provided by py_runtime; skip emit (§6)
    if module_id.startswith("pytra.built_in."):
        return ""
    return transpile_to_rust(east_doc)


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.rs MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/rs"
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

    return emit_all_modules(input_path, output_dir, ".rs", _transpile_rs, lang="rs")


if __name__ == "__main__":
    sys.exit(main())
