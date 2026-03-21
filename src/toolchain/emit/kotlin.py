#!/usr/bin/env python3
"""Kotlin backend: link-output.json → Kotlin multi-file output.

Usage:
    python3 -m toolchain.emit.kotlin LINK_OUTPUT.json --output-dir out/kotlin/
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path as NativePath

from toolchain.emit.kotlin.emitter import transpile_to_kotlin
from toolchain.emit.loader import emit_all_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_KT_RUNTIME_DIR = _ROOT / "sample" / "kotlin"
_KT_RUNTIME_FILES = ("py_runtime.kt", "image_runtime.kt")
_KT_NATIVE_STD_DIR = _ROOT / "src" / "runtime" / "kotlin" / "std"
_RUNTIME_EAST_ROOT = _ROOT / "src" / "runtime" / "east"


def _rewrite_extern_delegates(code: str, module_stem: str) -> str:
    """Rewrite @extern delegate calls in generated Kotlin runtime modules."""
    import re
    code = re.sub(
        r'\b' + re.escape(module_stem) + r'\.(\w+)\(',
        module_stem + r'_native_\1(',
        code,
    )
    code = re.sub(
        r'__pytra_float\((' + re.escape(module_stem) + r'_native_\w+\([^)]*\))\)',
        r'\1',
        code,
    )
    return code


def _generate_kotlin_runtime(output_dir: str) -> None:
    """Generate Kotlin runtime files from .east sources and copy native .kt files."""
    out = NativePath(output_dir)

    # 1. Copy py_runtime.kt and image_runtime.kt
    for name in _KT_RUNTIME_FILES:
        src = _KT_RUNTIME_DIR / name
        dst = out / name
        if src.exists() and not dst.exists():
            shutil.copy2(str(src), str(dst))

    # 2. Copy native std files (math_native.kt, time_native.kt)
    if _KT_NATIVE_STD_DIR.is_dir():
        for f in sorted(_KT_NATIVE_STD_DIR.iterdir()):
            if f.suffix == ".kt":
                d = out / f.name
                if not d.exists():
                    shutil.copy2(str(f), str(d))

    # 3. Transpile .east runtime modules to .kt (std/)
    _GENERATE_MODULES: dict[str, tuple[str, ...]] = {
        "std": ("time", "math"),
    }
    east_root = str(_RUNTIME_EAST_ROOT)
    if not os.path.isdir(east_root):
        return
    for bucket, allowed in _GENERATE_MODULES.items():
        bucket_dir = os.path.join(east_root, bucket)
        if not os.path.isdir(bucket_dir):
            continue
        for stem in allowed:
            east_file = os.path.join(bucket_dir, stem + ".east")
            if not os.path.isfile(east_file):
                continue
            dst_kt = out / (stem + ".kt")
            if dst_kt.exists():
                continue
            try:
                east_text = open(east_file, "r", encoding="utf-8").read()
                east_doc = json.loads(east_text)
                kt_text = transpile_to_kotlin(east_doc)
                kt_text = _rewrite_extern_delegates(kt_text, stem)
                dst_kt.write_text(kt_text, encoding="utf-8")
            except Exception:
                pass


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
    _generate_kotlin_runtime(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
