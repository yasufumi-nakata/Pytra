#!/usr/bin/env python3
"""JS backend: link-output.json → JS multi-file output.

Usage:
    python3 -m toolchain.emit.js LINK_OUTPUT.json --output-dir out/js/
"""

from __future__ import annotations

import sys

from toolchain.emit.js.emitter.js_emitter import transpile_to_js
from toolchain.emit.loader import emit_all_modules
from toolchain.misc.js_runtime_shims import write_js_runtime_shims


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.js LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/js"
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

    rc = emit_all_modules(input_path, output_dir, ".js", transpile_to_js)
    if rc != 0:
        return rc
    from pytra.std.pathlib import Path as PytraPath
    write_js_runtime_shims(PytraPath(output_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
