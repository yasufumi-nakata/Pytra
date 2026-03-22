#!/usr/bin/env python3
"""Swift backend: link-output.json → Swift multi-file output.

Usage:
    python3 -m toolchain.emit.swift LINK_OUTPUT.json --output-dir out/swift/
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path as NativePath

from toolchain.emit.swift.emitter import transpile_to_swift
from toolchain.emit.loader import emit_all_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_SWIFT_NATIVE_BUILTIN_DIR = _ROOT / "src" / "runtime" / "swift" / "built_in"
_SWIFT_NATIVE_STD_DIR = _ROOT / "src" / "runtime" / "swift" / "std"
_RUNTIME_EAST_ROOT = _ROOT / "src" / "runtime" / "east"


def _rewrite_extern_delegates(code: str, module_stem: str) -> str:
    """Rewrite @extern delegate calls in generated Swift runtime modules."""
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


def _strip_main(code: str) -> str:
    """Remove @main struct Main { static func main() { } } from generated Swift runtime modules."""
    import re
    # Remove @main annotation
    code = re.sub(r'@main\n', '', code)
    # Remove struct Main { static func main() { ... } }
    code = re.sub(r'struct Main \{[\s\S]*?\n\}\s*$', '', code)
    return code.rstrip() + "\n"


def _generate_swift_runtime(output_dir: str) -> None:
    """Generate Swift runtime files from .east sources and copy native .swift files."""
    out = NativePath(output_dir)

    # 1. Copy native runtime files from src/runtime/swift/built_in/
    if _SWIFT_NATIVE_BUILTIN_DIR.is_dir():
        for f in sorted(_SWIFT_NATIVE_BUILTIN_DIR.iterdir()):
            if f.suffix == ".swift":
                d = out / f.name
                if not d.exists():
                    shutil.copy2(str(f), str(d))

    # 2. Copy native std files (math_native.swift, time_native.swift)
    if _SWIFT_NATIVE_STD_DIR.is_dir():
        for f in sorted(_SWIFT_NATIVE_STD_DIR.iterdir()):
            if f.suffix == ".swift":
                d = out / f.name
                if not d.exists():
                    shutil.copy2(str(f), str(d))

    # 3. Transpile .east runtime modules to .swift (std/)
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
            dst_swift = out / (stem + ".swift")
            if dst_swift.exists():
                continue
            try:
                east_text = open(east_file, "r", encoding="utf-8").read()
                east_doc = json.loads(east_text)
                swift_text = transpile_to_swift(east_doc)
                swift_text = _rewrite_extern_delegates(swift_text, stem)
                swift_text = _strip_main(swift_text)
                dst_swift.write_text(swift_text, encoding="utf-8")
            except Exception:
                pass


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
    _generate_swift_runtime(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
