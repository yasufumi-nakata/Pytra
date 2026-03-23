#!/usr/bin/env python3
"""PHP backend: manifest.json → PHP multi-file output.

Usage:
    python3 -m toolchain.emit.php MANIFEST.json --output-dir out/php/
"""

from __future__ import annotations

import sys
from pathlib import Path

from toolchain.emit.php.emitter import transpile_to_php_native
from toolchain.emit.loader import emit_all_modules


def _overlay_native_std(output_dir: str) -> None:
    """No-op: @extern delegation in emitter + _native runtime files handle this.

    Previously this overwrote linker-generated std modules, but the emitter
    now generates proper __native_ delegation code.  The native seam files
    (std/time_native.php, std/math_native.php) are copied by copy_native_runtime.
    """
    pass


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.php MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/php"
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
        print("error: input manifest.json is required", file=sys.stderr)
        return 1

    rc = emit_all_modules(input_path, output_dir, ".php", transpile_to_php_native, lang="php")
    if rc != 0:
        return rc
    _overlay_native_std(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
