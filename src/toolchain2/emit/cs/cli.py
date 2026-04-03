#!/usr/bin/env python3
"""CLI helpers for toolchain2 C# emit from linked manifest output."""

from __future__ import annotations

from pytra.std import json
from pytra.std.json import JsonVal
from pytra.std.pathlib import Path

from toolchain2.emit.cs.emitter import emit_cs_module


def _copy_cs_runtime_files(output_dir: Path) -> int:
    """Copy C# runtime files into the emit directory."""
    runtime_root = Path(".").resolve().joinpath("src").joinpath("runtime").joinpath("cs")
    copied = 0
    if not runtime_root.exists():
        return copied
    built_in = runtime_root.joinpath("built_in").joinpath("py_runtime.cs")
    if built_in.exists():
        dst = output_dir.joinpath("built_in").joinpath("py_runtime.cs")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(built_in.read_text(encoding="utf-8"), encoding="utf-8")
        copied += 1
    std_dir = runtime_root.joinpath("std")
    if std_dir.exists():
        for cs_file in std_dir.glob("*.cs"):
            dst2 = output_dir.joinpath("std").joinpath(cs_file.name)
            dst2.parent.mkdir(parents=True, exist_ok=True)
            dst2.write_text(cs_file.read_text(encoding="utf-8"), encoding="utf-8")
            copied += 1
    return copied


def emit_cs_from_manifest(manifest_path: Path, output_dir: Path) -> int:
    manifest_doc = json.loads_obj(manifest_path.read_text(encoding="utf-8"))
    if manifest_doc is None:
        print("error: invalid manifest: " + str(manifest_path))
        return 1
    modules = manifest_doc.get_arr("modules")
    if modules is None:
        print("error: invalid manifest.modules: " + str(manifest_path))
        return 1
    output_dir.mkdir(parents=True, exist_ok=True)
    emitted = 0
    for item in modules.raw:
        item_obj = json.JsonValue(item).as_obj()
        if item_obj is None:
            continue
        module_id = item_obj.get_str("module_id")
        rel_output = item_obj.get_str("output")
        if module_id is None or module_id == "":
            continue
        if rel_output is None or rel_output == "":
            continue
        east_path = manifest_path.parent.joinpath(rel_output)
        if not east_path.exists():
            print("error: linked east3 missing: " + str(east_path))
            return 1
        east_doc_obj = json.loads_obj(east_path.read_text(encoding="utf-8"))
        if east_doc_obj is None:
            print("error: invalid east3 document: " + str(east_path))
            return 1
        code = emit_cs_module(east_doc_obj.raw)
        if code.strip() == "":
            continue
        out_path = output_dir.joinpath(module_id.replace(".", "_") + ".cs")
        out_path.write_text(code, encoding="utf-8")
        emitted += 1
    _copy_cs_runtime_files(output_dir)
    print("emitted: " + str(output_dir) + " (" + str(emitted) + " files)")
    return 0


def main(argv: list[str]) -> int:
    input_text = ""
    output_dir_text = ""
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "-o" or tok == "--output-dir":
            if i + 1 >= len(argv):
                print("error: missing value for " + tok)
                return 1
            output_dir_text = argv[i + 1]
            i += 2
            continue
        if tok == "-h" or tok == "--help":
            print("usage: python3 src/toolchain2/emit/cs/cli.py MANIFEST.json [-o OUTPUT_DIR]")
            return 0
        if not tok.startswith("-") and input_text == "":
            input_text = tok
        i += 1

    if input_text == "":
        print("error: manifest.json path is required")
        return 1

    manifest_path = Path(input_text)
    if manifest_path.name != "manifest.json":
        manifest_path = manifest_path.joinpath("manifest.json")
    if not manifest_path.exists():
        print("error: manifest.json not found: " + str(manifest_path))
        return 1

    if output_dir_text == "":
        output_dir_text = str(Path("work").joinpath("tmp").joinpath("emit").joinpath("cs"))
    return emit_cs_from_manifest(manifest_path, Path(output_dir_text))


if __name__ == "__main__":
    import sys as _stdlib_sys

    raise SystemExit(main(_stdlib_sys.argv[1:]))
