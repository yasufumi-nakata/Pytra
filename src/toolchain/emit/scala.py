#!/usr/bin/env python3
"""Scala backend: manifest.json → Scala single-file output.

All linked modules are merged into a single .scala file to avoid
top-level definition collisions in Scala 3.

Usage:
    python3 -m toolchain.emit.scala MANIFEST.json --output-dir out/scala/
"""

from __future__ import annotations

import sys
from pathlib import Path

from toolchain.emit.scala.emitter.scala_native_emitter import transpile_to_scala_native
from toolchain.emit.loader import copy_native_runtime, load_linked_modules


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.scala MANIFEST.json --output-dir DIR")
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
        print("error: input manifest.json is required", file=sys.stderr)
        return 1

    modules, entry_modules = load_linked_modules(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Collect all module sources: submodules first, then entry module
    submodule_sources: list[str] = []
    entry_source = ""
    entry_stem = ""

    for mod in modules:
        module_id = mod["module_id"]
        east_doc = mod["east_doc"]
        is_entry = mod.get("is_entry", False)

        if is_entry:
            entry_source = transpile_to_scala_native(east_doc, emit_main=True)
            entry_stem = module_id
        else:
            source = transpile_to_scala_native(east_doc, emit_main=False)
            submodule_sources.append("// --- module: " + module_id + " ---\n" + source)

    # Merge into single file
    merged_parts: list[str] = []
    # Collect unique import lines from all sources
    all_imports: set[str] = set()
    all_body_lines: list[str] = []

    for src in submodule_sources + [entry_source]:
        for line in src.split("\n"):
            stripped = line.strip()
            if stripped.startswith("import "):
                all_imports.add(stripped)
            else:
                all_body_lines.append(line)

    merged_parts.extend(sorted(all_imports))
    merged_parts.append("")
    merged_parts.extend(all_body_lines)

    merged = "\n".join(merged_parts)

    if entry_stem == "":
        entry_stem = "main"
    out_path = out / (entry_stem + ".scala")
    out_path.write_text(merged, encoding="utf-8")
    print("generated: " + str(out_path))

    copy_native_runtime(output_dir, "scala")
    return 0


if __name__ == "__main__":
    sys.exit(main())
