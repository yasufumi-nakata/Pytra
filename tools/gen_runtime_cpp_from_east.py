#!/usr/bin/env python3
"""Generate C++ .h/.cpp from all .east files in src/runtime/generated/.

This replaces the old gen_runtime_from_manifest.py for the simple case
of generating test-time C++ from pre-compiled .east files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from toolchain.emit.cpp.emitter import transpile_to_cpp
from toolchain.emit.cpp.emitter.header_builder import build_cpp_header_from_east


def _namespace_from_path(east_path: Path, generated_dir: Path) -> str:
    """Derive C++ namespace from .east file path relative to generated/.

    Examples:
        built_in/string_ops.east → pytra::built_in::string_ops
        std/pathlib.east         → pytra::std::pathlib
        utils/assertions.east    → pytra::utils::assertions
    """
    rel = east_path.relative_to(generated_dir).with_suffix("")
    parts = list(rel.parts)
    return "pytra::" + "::".join(parts)


def main() -> int:
    import re
    generated_dir = ROOT / "src" / "runtime" / "generated"
    east_files = sorted(generated_dir.rglob("*.east"))
    count = 0
    for east_path in east_files:
        east = json.loads(east_path.read_text(encoding="utf-8"))
        out_base = east_path.with_suffix("")
        ns = _namespace_from_path(east_path, generated_dir)
        cpp = transpile_to_cpp(east, top_namespace=ns)
        # Strip main() from generated .cpp — these are library modules, not executables.
        cpp = re.sub(r'\nint main\(int argc, char\*\* argv\) \{.*', '', cpp, flags=re.DOTALL)
        header = build_cpp_header_from_east(east, east_path, out_base.with_suffix(".h"), cpp_text=cpp, top_namespace=ns)
        # Add `using namespace` at end of header so native code can use unqualified names
        using_decl = f"\nusing namespace {ns};\n"
        # Insert before final #endif line
        lines = header.rstrip().split("\n")
        inserted = False
        for idx in range(len(lines) - 1, -1, -1):
            if lines[idx].strip().startswith("#endif"):
                lines.insert(idx, f"using namespace {ns};")
                inserted = True
                break
        if inserted:
            header = "\n".join(lines) + "\n"
        out_base.with_suffix(".cpp").write_text(cpp, encoding="utf-8")
        out_base.with_suffix(".h").write_text(header, encoding="utf-8")
        count += 1
    print(f"generated {count} .east → .h + .cpp pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
