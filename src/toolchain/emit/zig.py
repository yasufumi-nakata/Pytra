#!/usr/bin/env python3
"""Zig backend: link-output.json → Zig multi-file output.

Usage:
    python3 -m toolchain.emit.zig LINK_OUTPUT.json --output-dir out/zig/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from toolchain.emit.zig.emitter import transpile_to_zig_native
from toolchain.emit.loader import load_linked_modules

_RUNTIME_DIR = Path(__file__).resolve().parents[2] / "runtime" / "zig" / "built_in"
_STD_RUNTIME_DIR = Path(__file__).resolve().parents[2] / "runtime" / "zig" / "std"


def _copy_runtime(output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for f in _RUNTIME_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, out / f.name)
    # std native runtime を全サブモジュールディレクトリにコピー
    if _STD_RUNTIME_DIR.exists():
        for f in _STD_RUNTIME_DIR.iterdir():
            if f.is_file():
                for sub_dir in out.iterdir():
                    if sub_dir.is_dir():
                        shutil.copy2(f, sub_dir / f.name)


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.zig LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/zig"
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

    modules, entry_modules = load_linked_modules(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for mod in modules:
        module_id = mod["module_id"]
        east_doc = mod["east_doc"]
        is_entry = mod.get("is_entry", False)
        rel_path = module_id.replace(".", "/") + ".zig"
        out_path = out / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)

        is_submodule = not is_entry
        source = transpile_to_zig_native(east_doc, is_submodule=is_submodule)
        out_path.write_text(source, encoding="utf-8")
        print("generated: " + str(out_path))

    _copy_runtime(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
