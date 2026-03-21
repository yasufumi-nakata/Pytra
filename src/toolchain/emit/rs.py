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
_RS_RUNTIME_SRC = _ROOT / "sample" / "rs" / "py_runtime.rs"


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
    # Copy py_runtime.rs to output dir
    dst = NativePath(output_dir) / "py_runtime.rs"
    if _RS_RUNTIME_SRC.exists() and not dst.exists():
        shutil.copy2(str(_RS_RUNTIME_SRC), str(dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
