#!/usr/bin/env python3
"""CLI helpers for toolchain2 Rust emit from linked manifest output."""

from __future__ import annotations

import re

from pytra.std.json import JsonVal
from pytra.std.pathlib import Path

from toolchain2.emit.rs.emitter import emit_rs_module
from toolchain2.link.manifest_loader import load_linked_output


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _fqcn_to_tid_const(fqcn: str) -> str:
    flat = fqcn.replace(".", "_")
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", flat)
    snake = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", snake)
    return snake.upper() + "_TID"


def _generate_type_id_table_rs(type_id_table: dict[str, int]) -> str:
    lines: list[str] = []
    for fqcn, tid in sorted(type_id_table.items(), key=lambda kv: kv[1]):
        const_name = _fqcn_to_tid_const(fqcn)
        lines.append("pub const " + const_name + ": i64 = " + str(tid) + "_i64;")
    return "\n".join(lines) + ("\n" if len(lines) > 0 else "")


def _copy_rs_runtime_files(dst_dir: Path) -> int:
    runtime_root = _repo_root().joinpath("src").joinpath("runtime").joinpath("rs")
    copied = 0
    sources = [
        runtime_root.joinpath("built_in").joinpath("py_runtime.rs"),
        runtime_root.joinpath("std").joinpath("time_native.rs"),
        runtime_root.joinpath("std").joinpath("math_native.rs"),
    ]
    for src in sources:
        if not src.exists():
            continue
        dst = dst_dir.joinpath(src.name)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        copied += 1
    return copied


def _manifest_type_id_table(
    manifest_doc: dict[str, JsonVal],
    linked_modules: list[object],
) -> dict[str, int]:
    global_doc = manifest_doc.get("global")
    if isinstance(global_doc, dict):
        type_id_table = global_doc.get("type_id_table")
        if isinstance(type_id_table, dict):
            out: dict[str, int] = {}
            for fqcn, tid in type_id_table.items():
                if isinstance(fqcn, str) and isinstance(tid, int):
                    out[fqcn] = tid
            if len(out) > 0:
                return out

    dense_rows: list[tuple[str, int]] = []
    seen: set[str] = set()
    for module in linked_modules:
        east_doc = getattr(module, "east_doc", None)
        if not isinstance(east_doc, dict):
            continue
        meta = east_doc.get("meta")
        if not isinstance(meta, dict):
            continue
        lp = meta.get("linked_program_v1")
        if not isinstance(lp, dict):
            continue
        dense_map = lp.get("type_id_resolved_v1")
        if not isinstance(dense_map, dict):
            continue
        for fqcn, dense in dense_map.items():
            if not isinstance(fqcn, str) or not isinstance(dense, int):
                continue
            if fqcn.startswith("pytra.") or dense < 1000 or fqcn in seen:
                continue
            seen.add(fqcn)
            dense_rows.append((fqcn, dense))

    dense_rows.sort(key=lambda row: row[1])
    out: dict[str, int] = {}
    next_tid = 9
    for fqcn, _dense in dense_rows:
        out[fqcn] = next_tid
        next_tid += 1
    return out


def _write_rs_package_files(
    manifest_doc: dict[str, JsonVal],
    linked_modules: list[object],
    output_dir: Path,
) -> int:
    src_dir = output_dir.joinpath("src")
    src_dir.mkdir(parents=True, exist_ok=True)

    module_names: list[str] = []
    written = 0
    entry_mod = ""

    for module in linked_modules:
        east_doc = getattr(module, "east_doc", None)
        module_id = getattr(module, "module_id", "")
        is_entry = getattr(module, "is_entry", False)
        if not isinstance(east_doc, dict) or not isinstance(module_id, str) or module_id == "":
            continue
        code = emit_rs_module(east_doc, package_mode=True)
        if code.strip() == "":
            continue
        mod_name = module_id.replace(".", "_")
        src_dir.joinpath(mod_name + ".rs").write_text(code, encoding="utf-8")
        module_names.append(mod_name)
        written += 1
        if is_entry and entry_mod == "":
            entry_mod = mod_name

    written += _copy_rs_runtime_files(src_dir)
    for runtime_mod in ("py_runtime", "time_native", "math_native"):
        if src_dir.joinpath(runtime_mod + ".rs").exists() and runtime_mod not in module_names:
            module_names.append(runtime_mod)

    type_id_table = _manifest_type_id_table(manifest_doc, linked_modules)
    tid_src = _generate_type_id_table_rs(type_id_table)
    src_dir.joinpath("pytra_built_in_type_id_table.rs").write_text(tid_src, encoding="utf-8")
    module_names.append("pytra_built_in_type_id_table")
    written += 1

    lib_lines = [
        "pub mod " + mod_name + ";"
        for mod_name in sorted(set(module_names))
    ]
    src_dir.joinpath("lib.rs").write_text("\n".join(lib_lines) + "\n", encoding="utf-8")

    if entry_mod == "":
        raise RuntimeError("missing entry module for Rust package emit")
    main_src = "fn main() {\n"
    main_src += "    pytra_selfhost::" + entry_mod + "::main();\n"
    main_src += "}\n"
    src_dir.joinpath("main.rs").write_text(main_src, encoding="utf-8")

    cargo_src = "[package]\n"
    cargo_src += "name = \"pytra_selfhost\"\n"
    cargo_src += "version = \"0.1.0\"\n"
    cargo_src += "edition = \"2021\"\n"
    cargo_src += "\n"
    cargo_src += "[lib]\n"
    cargo_src += "name = \"pytra_selfhost\"\n"
    cargo_src += "path = \"src/lib.rs\"\n"
    cargo_src += "\n"
    cargo_src += "[[bin]]\n"
    cargo_src += "name = \"pytra_selfhost\"\n"
    cargo_src += "path = \"src/main.rs\"\n"
    output_dir.joinpath("Cargo.toml").write_text(cargo_src, encoding="utf-8")
    print("emitted: " + str(output_dir) + " (" + str(written) + " Rust files)")
    return 0


def emit_rs_from_manifest(manifest_path: Path, output_dir: Path, *, package_mode: bool = False) -> int:
    manifest_doc, linked_modules = load_linked_output(manifest_path)
    if package_mode:
        return _write_rs_package_files(manifest_doc, linked_modules, output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for module in linked_modules:
        code = emit_rs_module(module.east_doc)
        if code.strip() == "":
            continue
        fname = module.module_id.replace(".", "_") + ".rs"
        output_dir.joinpath(fname).write_text(code, encoding="utf-8")
        written += 1
    written += _copy_rs_runtime_files(output_dir)
    type_id_table = _manifest_type_id_table(manifest_doc, linked_modules)
    tid_rs = _generate_type_id_table_rs(type_id_table)
    if tid_rs != "" or not output_dir.joinpath("pytra_built_in_type_id_table.rs").exists():
        output_dir.joinpath("pytra_built_in_type_id_table.rs").write_text(tid_rs, encoding="utf-8")
        written += 1
    print("emitted: " + str(output_dir) + " (" + str(written) + " Rust files)")
    return 0


def main(argv: list[str]) -> int:
    input_text = ""
    output_dir_text = ""
    package_mode = False
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
        if tok == "--package":
            package_mode = True
            i += 1
            continue
        if tok == "-h" or tok == "--help":
            print("usage: python3 -m toolchain2.emit.rs.cli MANIFEST.json [-o OUTPUT_DIR] [--package]")
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
        output_dir_text = str(Path("work").joinpath("tmp").joinpath("emit").joinpath("rs"))
    return emit_rs_from_manifest(manifest_path, Path(output_dir_text), package_mode=package_mode)


if __name__ == "__main__":
    import sys as _stdlib_sys

    raise SystemExit(main(_stdlib_sys.argv[1:]))
