#!/usr/bin/env python3
"""CS backend: link-output.json → CS multi-file output.

Usage:
    python3 -m toolchain.emit.cs LINK_OUTPUT.json --output-dir out/cs/
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from toolchain.emit.cs.emitter.cs_emitter import transpile_to_csharp
from toolchain.emit.loader import load_linked_modules

_ROOT = Path(__file__).resolve().parents[3]
_RUNTIME_EAST_ROOT = _ROOT / "src" / "runtime" / "east"
_RUNTIME_CS_NATIVE_ROOT = _ROOT / "src" / "runtime" / "cs"


def _wrap_in_namespace(cs_text: str) -> str:
    """Wrap generated C# code in namespace Pytra.CsModule { ... }.

    Also replace bare @extern module calls (e.g. ``time.perf_counter()``)
    with their native class names (e.g. ``time_native.perf_counter()``).
    """
    # Replace bare extern calls: time.xxx → time_native.xxx, math.xxx → math_native.xxx
    import re
    for mod in ("time", "math", "sys", "os", "os_path", "glob"):
        cs_text = re.sub(
            r'\b' + mod + r'\.(\w)',
            mod + '_native.' + r'\1',
            cs_text,
        )
    lines = cs_text.split("\n")
    # Separate using statements from body
    using_lines: list[str] = []
    body_lines: list[str] = []
    in_body = False
    for line in lines:
        stripped = line.strip()
        if not in_body and (stripped.startswith("using ") or stripped == ""):
            using_lines.append(line)
        else:
            in_body = True
            body_lines.append("    " + line)
    result_lines = using_lines + ["", "namespace Pytra.CsModule", "{"] + body_lines + ["}"]
    return "\n".join(result_lines)


_EXTERN_CONSTANTS: dict[str, list[str]] = {
    "math": [
        "        public static double pi { get { return math_native.pi; } }",
        "        public static double e { get { return math_native.e; } }",
    ],
}


def _inject_extern_constants(cs_text: str, stem: str) -> str:
    """Insert extern constant properties into generated runtime classes."""
    lines = _EXTERN_CONSTANTS.get(stem)
    if not lines:
        return cs_text
    # Insert before the closing brace of the class
    # Find the last "    }" which closes the class body
    marker = "\n    }\n"
    pos = cs_text.rfind(marker)
    if pos < 0:
        return cs_text
    inject = "\n".join(lines) + "\n"
    return cs_text[:pos] + "\n" + inject + cs_text[pos:]


def _module_id_to_class_name(module_id: str) -> str:
    """モジュール ID からユニークなクラス名を生成する。

    例: "time/east" → "PytraModule_time_east"
    """
    safe = module_id.replace(".", "_").replace("/", "_").replace("-", "_")
    return "PytraModule_" + safe


def _emit_cs_modules(input_path: str, output_dir: str) -> int:
    """Link-output.json からモジュールを読み込み、C# multi-file emit する。

    entry module のみ Main を持つ Program クラスを生成し、
    sub-module は Main なしのユニーク名クラスを生成する。
    """
    modules, entry_modules = load_linked_modules(input_path)
    entry_set = set(entry_modules)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for mod in modules:
        module_id: str = mod["module_id"]
        east_doc: dict[str, Any] = mod["east_doc"]
        is_entry: bool = mod.get("is_entry", False) or module_id in entry_set

        rel_path = module_id.replace(".", "/") + ".cs"
        out_path = out / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if is_entry:
            source = transpile_to_csharp(east_doc, emit_main=True, class_name="Program")
        else:
            class_name = _module_id_to_class_name(module_id)
            source = transpile_to_csharp(east_doc, emit_main=False, class_name=class_name)

        out_path.write_text(source, encoding="utf-8")
        print("generated: " + str(out_path))

    return 0


def _generate_cs_runtime(output_dir: str) -> None:
    """Generate CS runtime files from .east sources and copy native .cs files."""
    out = Path(output_dir)

    # 1. Copy native runtime .cs files (built_in/, std/)
    #    Only copy files that have matching generated modules or are always needed.
    _NATIVE_ALLOW: dict[str, tuple[str, ...]] = {
        "built_in": ("py_runtime.cs",),
        "std": ("time_native.cs", "math_native.cs"),
    }
    for subdir, allowed_files in _NATIVE_ALLOW.items():
        src_dir = _RUNTIME_CS_NATIVE_ROOT / subdir
        if not src_dir.is_dir():
            continue
        dst_dir = out / subdir
        dst_dir.mkdir(parents=True, exist_ok=True)
        for name in allowed_files:
            src_file = src_dir / name
            if src_file.exists():
                shutil.copy2(str(src_file), str(dst_dir / name))

    # 2. Transpile .east runtime modules to .cs (generated/std/, generated/utils/)
    #    Only modules with a native counterpart or known to compile cleanly
    #    are generated.  The rest are deferred until the emitter matures.
    _GENERATE_MODULES: dict[str, tuple[str, ...]] = {
        "std": ("time", "math"),
        "utils": ("png", "gif"),
    }
    east_root = str(_RUNTIME_EAST_ROOT)
    if not os.path.isdir(east_root):
        return
    for bucket, allowed in _GENERATE_MODULES.items():
        bucket_dir = os.path.join(east_root, bucket)
        if not os.path.isdir(bucket_dir):
            continue
        dst_dir = out / "generated" / bucket
        dst_dir.mkdir(parents=True, exist_ok=True)
        for stem in allowed:
            east_file = os.path.join(bucket_dir, stem + ".east")
            if not os.path.isfile(east_file):
                continue
            dst_cs = dst_dir / (stem + ".cs")
            if dst_cs.exists():
                continue
            # utils modules use "_helper" suffix (e.g. png_helper, gif_helper)
            # to match emitter's _module_alias_target convention.
            if bucket == "utils":
                class_name = stem + "_helper"
            else:
                class_name = stem  # e.g. "time", "math" — matches Pytra.CsModule.time
            try:
                east_text = open(east_file, "r", encoding="utf-8").read()
                east_doc = json.loads(east_text)
                cs_text = transpile_to_csharp(east_doc, emit_main=False, class_name=class_name)
                # Wrap in Pytra.CsModule namespace so user code can
                # reference as Pytra.CsModule.time.perf_counter() etc.
                cs_text = _wrap_in_namespace(cs_text)
                # Inject missing extern constants that the emitter
                # does not generate from @extern Assign nodes.
                cs_text = _inject_extern_constants(cs_text, stem)
                dst_cs.write_text(cs_text, encoding="utf-8")
            except Exception:
                pass


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.cs LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/cs"
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

    rc = _emit_cs_modules(input_path, output_dir)
    if rc != 0:
        return rc
    _generate_cs_runtime(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
