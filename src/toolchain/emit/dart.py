#!/usr/bin/env python3
"""Standalone DART backend: EAST3 JSON / link-output.json → DART source.

Usage:
    python3 -m toolchain.emit.dart INPUT.json -o out/output.dart
    python3 -m toolchain.emit.dart link-output.json --output-dir out/dart/
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from toolchain.emit.dart.emitter import transpile_to_dart_native

_RUNTIME_DIR = Path(__file__).resolve().parent.parent.parent / "runtime" / "dart" / "built_in"


def _is_link_output(doc: dict) -> bool:
    return "modules" in doc and "entry_modules" in doc


def _copy_runtime(dest_dir: Path) -> None:
    """Copy py_runtime.dart to the output directory."""
    src = _RUNTIME_DIR / "py_runtime.dart"
    if src.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest_dir / "py_runtime.dart"))


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.dart INPUT.json -o OUTPUT.dart")
        return 0

    input_path = ""
    output_path = ""
    output_dir = ""
    i = 0
    while i < len(argv):
        tok = argv[i]
        if (tok == "-o" or tok == "--output") and i + 1 < len(argv):
            output_path = argv[i + 1]
            i += 2
            continue
        if tok == "--output-dir" and i + 1 < len(argv):
            output_dir = argv[i + 1]
            i += 2
            continue
        if not tok.startswith("-") and input_path == "":
            input_path = tok
        i += 1

    if input_path == "":
        print("error: input file is required", file=sys.stderr)
        return 1

    doc = json.loads(Path(input_path).read_text(encoding="utf-8"))

    if _is_link_output(doc):
        # link-output.json: extract entry module EAST doc
        from toolchain.link import load_linked_output_bundle
        _manifest, linked_modules = load_linked_output_bundle(Path(input_path))
        entry_modules_any = doc.get("entry_modules", [])
        entry_set = set(entry_modules_any) if isinstance(entry_modules_any, list) else set()
        if output_dir == "":
            output_dir = "out/dart"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for module in linked_modules:
            if not module.is_entry:
                continue
            if entry_set and module.module_id not in entry_set:
                continue
            source = transpile_to_dart_native(module.east_doc)
            stem = Path(module.source_path).stem if module.source_path else module.module_id
            out_file = Path(output_dir) / (stem + ".dart")
            out_file.write_text(source, encoding="utf-8")
            print("generated: " + str(out_file))
        _copy_runtime(Path(output_dir))
        return 0

    # Single EAST3 JSON
    if output_path == "":
        output_path = Path(input_path).stem + ".dart"
    source = transpile_to_dart_native(doc)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(source, encoding="utf-8")
    _copy_runtime(Path(output_path).parent)
    print("generated: " + output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
