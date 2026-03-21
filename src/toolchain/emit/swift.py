#!/usr/bin/env python3
"""Swift backend: link-output.json → Swift multi-file output.

Usage:
    python3 -m toolchain.emit.swift LINK_OUTPUT.json --output-dir out/swift/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path as NativePath

from toolchain.emit.swift.emitter import transpile_to_swift
from toolchain.emit.loader import emit_all_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_SWIFT_RUNTIME_DIR = _ROOT / "sample" / "swift"
_SWIFT_RUNTIME_FILES = ("py_runtime.swift",)
_SWIFT_NATIVE_STD_DIR = _ROOT / "src" / "runtime" / "swift" / "std"


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.swift LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/swift"
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

    rc = emit_all_modules(input_path, output_dir, ".swift", transpile_to_swift)
    if rc != 0:
        return rc
    out = NativePath(output_dir)
    for name in _SWIFT_RUNTIME_FILES:
        src = _SWIFT_RUNTIME_DIR / name
        dst = out / name
        if src.exists() and not dst.exists():
            shutil.copy2(str(src), str(dst))
    # Copy native std files (math_native.swift, time_native.swift)
    if _SWIFT_NATIVE_STD_DIR.is_dir():
        for f in sorted(_SWIFT_NATIVE_STD_DIR.iterdir()):
            if f.suffix == ".swift":
                d = out / f.name
                if not d.exists():
                    shutil.copy2(str(f), str(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
