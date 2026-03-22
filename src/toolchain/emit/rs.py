#!/usr/bin/env python3
"""RS backend: link-output.json → RS multi-file output.

Usage:
    python3 -m toolchain.emit.rs LINK_OUTPUT.json --output-dir out/rs/
"""

from __future__ import annotations

import sys

import shutil
from pathlib import Path as NativePath

from toolchain.emit.rs.emitter.rs_emitter import transpile_to_rust
from toolchain.emit.loader import emit_all_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_RS_NATIVE_BUILTIN_DIR = _ROOT / "src" / "runtime" / "rs" / "built_in"
_RS_NATIVE_STD_DIR = _ROOT / "src" / "runtime" / "rs" / "std"


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.rs LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/rs"
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

    rc = emit_all_modules(input_path, output_dir, ".rs", transpile_to_rust)
    if rc != 0:
        return rc
    # Copy native runtime files from src/runtime/rs/
    out = NativePath(output_dir)
    for subdir in ("built_in", "std"):
        src_dir = _RS_NATIVE_BUILTIN_DIR.parent / subdir if subdir == "built_in" else _RS_NATIVE_STD_DIR
        if src_dir.is_dir():
            for f in sorted(src_dir.iterdir()):
                if f.suffix == ".rs":
                    d = out / f.name
                    if not d.exists():
                        shutil.copy2(str(f), str(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
