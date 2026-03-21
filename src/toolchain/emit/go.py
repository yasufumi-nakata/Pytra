#!/usr/bin/env python3
"""Go backend: link-output.json → Go multi-file output.

Usage:
    python3 -m toolchain.emit.go LINK_OUTPUT.json --output-dir out/go/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path as NativePath

from toolchain.emit.go.emitter import transpile_to_go
from toolchain.emit.loader import emit_all_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_GO_RUNTIME_SRC = _ROOT / "sample" / "go" / "py_runtime.go"
_GO_NATIVE_STD_DIR = _ROOT / "src" / "runtime" / "go" / "std"


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.go LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/go"
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

    rc = emit_all_modules(input_path, output_dir, ".go", transpile_to_go)
    if rc != 0:
        return rc
    out = NativePath(output_dir)
    dst = out / "py_runtime.go"
    if _GO_RUNTIME_SRC.exists() and not dst.exists():
        shutil.copy2(str(_GO_RUNTIME_SRC), str(dst))
    # Copy native std files (math_native.go, time_native.go)
    if _GO_NATIVE_STD_DIR.is_dir():
        for f in sorted(_GO_NATIVE_STD_DIR.iterdir()):
            if f.suffix == ".go":
                d = out / f.name
                if not d.exists():
                    shutil.copy2(str(f), str(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
