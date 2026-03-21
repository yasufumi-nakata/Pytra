#!/usr/bin/env python3
"""Kotlin backend: link-output.json → Kotlin multi-file output.

Usage:
    python3 -m toolchain.emit.kotlin LINK_OUTPUT.json --output-dir out/kotlin/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path as NativePath

from toolchain.emit.kotlin.emitter import transpile_to_kotlin
from toolchain.emit.loader import emit_all_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_KT_RUNTIME_DIR = _ROOT / "sample" / "kotlin"
_KT_RUNTIME_FILES = ("py_runtime.kt", "image_runtime.kt")
_KT_NATIVE_STD_DIR = _ROOT / "src" / "runtime" / "kotlin" / "std"


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.kotlin LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/kotlin"
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

    rc = emit_all_modules(input_path, output_dir, ".kt", transpile_to_kotlin)
    if rc != 0:
        return rc
    out = NativePath(output_dir)
    for name in _KT_RUNTIME_FILES:
        src = _KT_RUNTIME_DIR / name
        dst = out / name
        if src.exists() and not dst.exists():
            shutil.copy2(str(src), str(dst))
    # Copy native std files (math_native.kt, time_native.kt)
    if _KT_NATIVE_STD_DIR.is_dir():
        for f in sorted(_KT_NATIVE_STD_DIR.iterdir()):
            if f.suffix == ".kt":
                d = out / f.name
                if not d.exists():
                    shutil.copy2(str(f), str(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
