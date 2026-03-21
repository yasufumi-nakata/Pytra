#!/usr/bin/env python3
"""Java backend: link-output.json → Java multi-file output.

Usage:
    python3 -m toolchain.emit.java LINK_OUTPUT.json --output-dir out/java/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path as NativePath
from typing import Any

from toolchain.emit.java.emitter import transpile_to_java
from toolchain.emit.loader import load_linked_modules

_ROOT = NativePath(__file__).resolve().parents[3]
_JAVA_RUNTIME_DIR = _ROOT / "sample" / "java"
_JAVA_SRC_RUNTIME_DIR = _ROOT / "src" / "runtime" / "java"


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


def _copy_java_runtime(output_dir: str) -> None:
    """Copy required Java runtime files."""
    out = NativePath(output_dir)
    # Copy PyRuntime from src/runtime/java/ (authoritative, has PyFile/open)
    py_rt_src = _JAVA_SRC_RUNTIME_DIR / "built_in" / "PyRuntime.java"
    py_rt_dst = out / "PyRuntime.java"
    if py_rt_src.exists() and not py_rt_dst.exists():
        shutil.copy2(str(py_rt_src), str(py_rt_dst))
    # Copy additional runtime files from sample/java/
    _JAVA_SAMPLE_RUNTIME_FILES = (
        "png.java",
        "gif.java",
        "time.java",
        "time_native.java",
        "math.java",
        "math_native.java",
    )
    for name in _JAVA_SAMPLE_RUNTIME_FILES:
        src = _JAVA_RUNTIME_DIR / name
        dst = out / name
        if src.exists() and not dst.exists():
            shutil.copy2(str(src), str(dst))


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.java LINK_OUTPUT.json --output-dir DIR")
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
        print("error: input link-output.json is required", file=sys.stderr)
        return 1

    rc = _emit_java_modules(input_path, output_dir)
    if rc != 0:
        return rc
    _copy_java_runtime(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
