"""Runtime module discovery: transitive closure of import dependencies.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
ロジック参照元: toolchain/link/program_loader.py (import はしない)。
"""

from __future__ import annotations

from pytra.std.json import JsonVal
from pytra.std.pathlib import Path
from pytra.std import json


_RUNTIME_EAST_ROOT = Path(__file__).resolve().parents[2] / "runtime" / "east"

_RUNTIME_MODULE_BUCKETS: dict[str, str] = {
    "pytra.built_in.": "built_in",
    "pytra.std.": "std",
    "pytra.utils.": "utils",
}


def resolve_runtime_east_path(module_id: str) -> str:
    """Resolve a runtime module_id to its .east file path, or empty string."""
    for prefix, bucket in _RUNTIME_MODULE_BUCKETS.items():
        if module_id.startswith(prefix):
            name = module_id[len(prefix):]
            east_path = _RUNTIME_EAST_ROOT / bucket / (name + ".east")
            if east_path.exists():
                return str(east_path)
    # Fallback: bare module name → pytra.std.X
    bare_path = _RUNTIME_EAST_ROOT / "std" / (module_id + ".east")
    if bare_path.exists():
        return str(bare_path)
    return ""


def _is_explicit_runtime_module(module_id: str) -> bool:
    for prefix in _RUNTIME_MODULE_BUCKETS.keys():
        if module_id.startswith(prefix):
            return True
    return False


def _resolve_runtime_dep_or_fail(module_id: str, *, required: bool = True) -> str:
    """Resolve a runtime dependency path and fail closed for required runtime IDs."""
    east_path = resolve_runtime_east_path(module_id)
    if east_path != "":
        return east_path
    if required and _is_explicit_runtime_module(module_id):
        raise RuntimeError("input_invalid: runtime EAST module not found: " + module_id)
    return ""


def _has_format_spec(node: JsonVal) -> bool:
    """EAST ノードツリーに format_spec を持つ FormattedValue が含まれるか再帰検査。"""
    if isinstance(node, dict):
        if node.get("kind") == "FormattedValue":
            fs = node.get("format_spec")
            if isinstance(fs, str) and fs != "":
                return True
        for v in node.values():
            if _has_format_spec(v):
                return True
    elif isinstance(node, list):
        for item in node:
            if _has_format_spec(item):
                return True
    return False


def _load_east_file(path_str: str) -> dict[str, JsonVal]:
    """Load a .east file as a JSON dict."""
    try:
        text = Path(path_str).read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError("failed to read runtime EAST: " + path_str + ": " + str(exc)) from exc
    try:
        obj = json.loads(text).raw
    except Exception as exc:
        raise RuntimeError("failed to parse runtime EAST: " + path_str + ": " + str(exc)) from exc
    if not isinstance(obj, dict):
        raise RuntimeError("invalid runtime EAST document: " + path_str)
    return obj


def _append_runtime_dep(
    new_deps: list[tuple[str, str]],
    seen_paths: set[str],
    module_id: str,
    *,
    required: bool = True,
) -> None:
    """Resolve and queue a runtime dependency if needed."""
    east_path = _resolve_runtime_dep_or_fail(module_id, required=required)
    if east_path != "" and east_path not in seen_paths:
        new_deps.append((east_path, east_path))


def discover_runtime_modules(
    module_map: dict[str, dict[str, JsonVal]],
) -> dict[str, dict[str, JsonVal]]:
    """Scan module_map for runtime imports and add their .east files.

    Iterates until no new runtime dependencies are found (transitive closure).
    """
    result: dict[str, dict[str, JsonVal]] = dict(module_map)
    seen_paths: set[str] = set(result.keys())

    changed = True
    while changed:
        changed = False
        new_deps: list[tuple[str, str]] = []  # (path_str, path_str)

        for east_doc in list(result.values()):
            if not isinstance(east_doc, dict):
                continue

            # Scan meta.import_bindings
            meta_val = east_doc.get("meta")
            if isinstance(meta_val, dict):
                bindings_val = meta_val.get("import_bindings")
                if isinstance(bindings_val, list):
                    for binding in bindings_val:
                        if not isinstance(binding, dict):
                            continue
                        mod_id = binding.get("module_id")
                        if isinstance(mod_id, str) and mod_id != "":
                            _append_runtime_dep(new_deps, seen_paths, mod_id, required=True)

            # Scan body for Import/ImportFrom
            body_val = east_doc.get("body")
            if isinstance(body_val, list):
                for stmt in body_val:
                    if not isinstance(stmt, dict):
                        continue
                    kind = stmt.get("kind")
                    if kind == "ImportFrom":
                        mod = stmt.get("module")
                        if isinstance(mod, str) and mod != "":
                            _append_runtime_dep(new_deps, seen_paths, mod, required=True)
                            # Sub-module imports: from pytra.utils import png → pytra.utils.png
                            names_val = stmt.get("names")
                            if isinstance(names_val, list):
                                for ent in names_val:
                                    if isinstance(ent, dict):
                                        sym = ent.get("name")
                                        if isinstance(sym, str) and sym != "":
                                            sub_mod = mod + "." + sym
                                            _append_runtime_dep(new_deps, seen_paths, sub_mod, required=False)
                    elif kind == "Import":
                        names_val = stmt.get("names")
                        if isinstance(names_val, list):
                            for ent in names_val:
                                if isinstance(ent, dict):
                                    name_val = ent.get("name")
                                    if isinstance(name_val, str):
                                        _append_runtime_dep(new_deps, seen_paths, name_val, required=True)

            # Detect implicit format_value dependency from f-string
            if _has_format_spec(east_doc):
                _append_runtime_dep(new_deps, seen_paths, "pytra.built_in.format_value", required=True)

        for path_str, _ in new_deps:
            if path_str in seen_paths:
                continue
            seen_paths.add(path_str)
            doc = _load_east_file(path_str)
            result[path_str] = doc
            changed = True

    return result
