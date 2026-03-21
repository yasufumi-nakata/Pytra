#!/usr/bin/env python3
"""Scala backend: link-output.json → Scala multi-file output.

Usage:
    python3 -m toolchain.emit.scala LINK_OUTPUT.json --output-dir out/scala/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from toolchain.emit.scala.emitter import transpile_to_scala_native
from toolchain.emit.loader import load_linked_modules


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.scala LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/scala"
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
        print("error: input link-output.json is required", file=sys.stderr)
        return 1

    modules, entry_modules = load_linked_modules(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for mod in modules:
        module_id = mod["module_id"]
        east_doc = mod["east_doc"]
        is_entry = mod.get("is_entry", False)
        rel_path = module_id.replace(".", "/") + ".scala"
        out_path = out / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)

        source = transpile_to_scala_native(east_doc, emit_main=is_entry)
        out_path.write_text(source, encoding="utf-8")
        print("generated: " + str(out_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
