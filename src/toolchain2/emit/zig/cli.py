#!/usr/bin/env python3
"""CLI helpers for toolchain2 Zig emit from linked manifest output."""

from __future__ import annotations

from pytra.std import json
from pytra.std.json import JsonVal
from pytra.std.pathlib import Path

from toolchain2.emit.zig.emitter import emit_zig_module


def _zig_rel_output_path(module_id: str) -> Path:
    rel_module = module_id
    if rel_module.startswith("pytra."):
        rel_module = rel_module[len("pytra."):]
    return Path(rel_module.replace(".", "/") + ".zig")


def _inject_zig_emit_context(
    east_doc: dict[str, JsonVal],
    module_id: str,
    *,
    is_entry: bool,
) -> None:
    meta = east_doc.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        east_doc["meta"] = meta
    rel_path = _zig_rel_output_path(module_id)
    depth = len(rel_path.parts) - 1
    root_rel_prefix = "../" * depth if depth > 0 else "./"
    meta["emit_context"] = {
        "module_id": module_id,
        "root_rel_prefix": root_rel_prefix,
        "is_entry": is_entry,
    }


def _copy_zig_runtime_files(output_dir: Path) -> int:
    """Copy Zig runtime files preserving built_in/std layout."""
    runtime_root = Path(".").resolve().joinpath("src").joinpath("runtime").joinpath("zig")
    copied = 0
    py_runtime_text = ""
    py_runtime_src = runtime_root.joinpath("built_in").joinpath("py_runtime.zig")
    if py_runtime_src.exists():
        py_runtime_text = py_runtime_src.read_text(encoding="utf-8")
    for bucket in ["built_in", "std"]:
        bucket_dir = runtime_root.joinpath(bucket)
        if not bucket_dir.exists():
            continue
        for zig_file in bucket_dir.glob("*.zig"):
            dst = output_dir.joinpath(bucket).joinpath(zig_file.name)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(zig_file.read_text(encoding="utf-8"), encoding="utf-8")
            copied += 1
    if py_runtime_text != "":
        core_dst = output_dir.joinpath("core").joinpath("py_runtime.zig")
        core_dst.parent.mkdir(parents=True, exist_ok=True)
        core_dst.write_text(py_runtime_text, encoding="utf-8")
        copied += 1
    return copied


def emit_zig_from_manifest(manifest_path: Path, output_dir: Path) -> int:
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
        if module_id is None or module_id == "" or rel_output is None or rel_output == "":
            continue
        east_path = manifest_path.parent.joinpath(rel_output)
        if not east_path.exists():
            print("error: linked east3 missing: " + str(east_path))
            return 1
        east_doc_obj = json.loads_obj(east_path.read_text(encoding="utf-8"))
        if east_doc_obj is None:
            print("error: invalid east3 document: " + str(east_path))
            return 1
        is_entry = bool(item_obj.get_bool("is_entry"))
        if not is_entry:
            source_path_val = east_doc_obj.raw.get("source_path")
            if isinstance(source_path_val, str):
                is_entry = Path(source_path_val).stem == module_id.rsplit(".", 1)[-1]
        _inject_zig_emit_context(east_doc_obj.raw, module_id, is_entry=is_entry)
        code = emit_zig_module(east_doc_obj.raw)
        if code.strip() == "":
            continue
        out_path = output_dir.joinpath(_zig_rel_output_path(module_id))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(code, encoding="utf-8")
        emitted += 1
    _copy_zig_runtime_files(output_dir)
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
            print("usage: python3 src/toolchain2/emit/zig/cli.py MANIFEST.json [-o OUTPUT_DIR]")
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
        output_dir_text = str(Path("work").joinpath("tmp").joinpath("emit").joinpath("zig"))
    return emit_zig_from_manifest(manifest_path, Path(output_dir_text))


if __name__ == "__main__":
    import sys as _stdlib_sys

    raise SystemExit(main(_stdlib_sys.argv[1:]))
