#!/usr/bin/env python3
"""Java backend: manifest.json → Java multi-file output.

Usage:
    python3 -m toolchain.emit.java MANIFEST.json --output-dir out/java/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path as NativePath
from typing import Any

from toolchain.emit.java.emitter import transpile_to_java
from toolchain.emit.loader import copy_native_runtime, load_linked_modules


def _emit_java_modules(input_path: str, output_dir: str) -> int:
    """Load linked modules and emit Java files.

    Entry module is emitted as Main.java (Java requires filename == class name).
    """
    modules, entry_modules = load_linked_modules(input_path)
    entry_set = set(entry_modules)
    out = NativePath(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for mod in modules:
        module_id: str = mod["module_id"]
        east_doc: dict[str, Any] = mod["east_doc"]
        is_entry: bool = mod.get("is_entry", False) or module_id in entry_set

        source = transpile_to_java(east_doc)

        if is_entry:
            # Java requires public class Main → Main.java
            out_path = out / "Main.java"
        else:
            rel_path = module_id.replace(".", "/") + ".java"
            out_path = out / rel_path

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(source, encoding="utf-8")
        print("generated: " + str(out_path))

    return 0




def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.java MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/java"
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

    rc = _emit_java_modules(input_path, output_dir)
    if rc != 0:
        return rc
    copy_native_runtime(output_dir, "java")
    return 0


if __name__ == "__main__":
    sys.exit(main())
