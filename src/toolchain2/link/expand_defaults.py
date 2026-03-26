"""Cross-module default argument expansion for linked programs.

Link 段で全 module の FunctionDef から arg_defaults を収集し、
Call ノードの引数が不足している場合にデフォルト値を補完する。

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.common.jv import deep_copy_json
from toolchain2.link.import_maps import collect_import_maps


def _module_id_from_doc(doc: dict[str, JsonVal]) -> str:
    """Extract module_id from linked metadata or raw EAST meta."""
    meta = doc.get("meta")
    if not isinstance(meta, dict):
        return ""
    lp = meta.get("linked_program_v1")
    if isinstance(lp, dict):
        mid = lp.get("module_id")
        if isinstance(mid, str) and mid != "":
            return mid
    mid2 = meta.get("module_id")
    if isinstance(mid2, str):
        return mid2
    return ""


def _collect_all_fn_sigs(modules: list[dict[str, JsonVal]]) -> dict[str, dict[str, JsonVal]]:
    """Collect function signatures from all modules.

    Returns: {"<module_id>::<fn_name>": {"arg_order": [...], "arg_defaults": {...}}}
    """
    sigs: dict[str, dict[str, JsonVal]] = {}
    for doc in modules:
        if not isinstance(doc, dict):
            continue
        module_id = _module_id_from_doc(doc)
        if module_id == "":
            continue

        body = doc.get("body")
        if not isinstance(body, list):
            continue
        for stmt in body:
            if not isinstance(stmt, dict):
                continue
            _collect_sig(stmt, sigs, module_id, "")

    return sigs


def _collect_sig(
    node: dict[str, JsonVal],
    sigs: dict[str, dict[str, JsonVal]],
    module_id: str,
    class_name: str,
) -> None:
    kind = node.get("kind")
    if kind == "FunctionDef":
        name = node.get("name")
        if not isinstance(name, str) or name == "":
            return
        if module_id == "":
            return
        ao = node.get("arg_order")
        ad = node.get("arg_defaults")
        if not isinstance(ao, list):
            return
        sig: dict[str, JsonVal] = {
            "arg_order": ao,
            "arg_defaults": ad if isinstance(ad, dict) else {},
        }
        full = class_name + "." + name if class_name != "" else name
        sigs[module_id + "::" + full] = sig

        # Recurse into nested functions
        body = node.get("body")
        if isinstance(body, list):
            for s in body:
                if isinstance(s, dict):
                    _collect_sig(s, sigs, module_id, "")

    elif kind == "ClassDef":
        cn = node.get("name")
        if not isinstance(cn, str):
            return
        body = node.get("body")
        if isinstance(body, list):
            for s in body:
                if isinstance(s, dict):
                    _collect_sig(s, sigs, module_id, cn)


def _resolve_call_sig_key(
    node: dict[str, JsonVal],
    *,
    current_module_id: str,
    import_modules: dict[str, str],
    import_symbols: dict[str, str],
) -> str:
    """Resolve a Call node to a qualified signature key.

    Cross-module default expansion is intentionally conservative:
    only direct same-module calls, imported-symbol calls, and explicit
    module-alias calls are resolved. Method calls on arbitrary receivers
    are left untouched to avoid ambiguous expansion.
    """
    func = node.get("func")
    if not isinstance(func, dict):
        return ""

    fk = func.get("kind")
    if fk == "Name":
        fn_id = func.get("id")
        if isinstance(fn_id, str) and fn_id != "":
            imported = import_symbols.get(fn_id)
            if isinstance(imported, str) and imported != "":
                return imported
            if current_module_id != "":
                return current_module_id + "::" + fn_id
        return ""

    if fk == "Attribute":
        attr = func.get("attr")
        owner = func.get("value")
        if not isinstance(attr, str) or attr == "" or not isinstance(owner, dict):
            return ""
        if owner.get("kind") != "Name":
            return ""
        owner_id = owner.get("id")
        if not isinstance(owner_id, str) or owner_id == "":
            return ""
        module_id = import_modules.get(owner_id, "")
        if module_id == "":
            owner_rt = owner.get("resolved_type")
            if isinstance(owner_rt, str) and owner_rt != "":
                # First try any imported class symbol that matches the receiver type.
                for imported in import_symbols.values():
                    if not isinstance(imported, str) or "::" not in imported:
                        continue
                    mod, export = imported.split("::", 1)
                    if export == owner_rt:
                        if mod.startswith("pytra."):
                            return mod + "::" + export + "." + attr
                        if mod != "":
                            return "pytra.std." + mod + "::" + export + "." + attr
                        return mod + "::" + export + "." + attr
                # Then try a local-class method in the current module.
                if current_module_id != "":
                    return current_module_id + "::" + owner_rt + "." + attr
            return ""
        return module_id + "::" + attr

    return ""


def _expand_walk(
    node: JsonVal,
    sigs: dict[str, dict[str, JsonVal]],
    *,
    current_module_id: str,
    import_modules: dict[str, str],
    import_symbols: dict[str, str],
) -> None:
    """Recursively walk the AST and expand default arguments in Call nodes."""
    if isinstance(node, list):
        for item in node:
            _expand_walk(
                item,
                sigs,
                current_module_id=current_module_id,
                import_modules=import_modules,
                import_symbols=import_symbols,
            )
        return
    if not isinstance(node, dict):
        return

    if node.get("kind") == "Call":
        sig_key = _resolve_call_sig_key(
            node,
            current_module_id=current_module_id,
            import_modules=import_modules,
            import_symbols=import_symbols,
        )
        if sig_key != "" and sig_key in sigs:
            sig = sigs[sig_key]
            ao = sig.get("arg_order")
            ad = sig.get("arg_defaults")
            args = node.get("args")
            if isinstance(args, list) and isinstance(ao, list) and isinstance(ad, dict):
                # Exclude 'self' from expected params
                expected: list[str] = []
                for p in ao:
                    if isinstance(p, str) and p != "self":
                        expected.append(p)
                n_expected = len(expected)

                # Collect keyword args
                kw_map: dict[str, JsonVal] = {}
                kws = node.get("keywords")
                if isinstance(kws, list):
                    for kw in kws:
                        if isinstance(kw, dict):
                            ka = kw.get("arg")
                            kv = kw.get("value")
                            if isinstance(ka, str) and ka != "":
                                kw_map[ka] = kv

                # Fill missing args from defaults
                if len(args) < n_expected:
                    for i in range(len(args), n_expected):
                        param_name = expected[i]
                        if param_name in kw_map:
                            kv2 = kw_map[param_name]
                            args.append(deep_copy_json(kv2) if isinstance(kv2, (dict, list)) else kv2)
                        elif param_name in ad:
                            default_val = ad[param_name]
                            if isinstance(default_val, (dict, list)):
                                args.append(deep_copy_json(default_val))
                            else:
                                args.append(default_val)
                if len(kw_map) > 0:
                    node["keywords"] = []

    for v in node.values():
        if isinstance(v, (dict, list)):
            _expand_walk(
                v,
                sigs,
                current_module_id=current_module_id,
                import_modules=import_modules,
                import_symbols=import_symbols,
            )


def expand_cross_module_defaults(
    modules_with_ids: list[tuple[str, dict[str, JsonVal]] | dict[str, JsonVal]],
) -> None:
    """Expand default arguments in Call nodes across all linked modules.

    Args:
        modules_with_ids: list of (module_id, east_doc) tuples or plain docs.

    Mutates the east_doc of each module in-place.
    """
    # Collect signatures from all modules (using explicit module_id)
    sigs: dict[str, dict[str, JsonVal]] = {}
    normalized: list[tuple[str, dict[str, JsonVal]]] = []
    for entry in modules_with_ids:
        if isinstance(entry, tuple) and len(entry) == 2:
            module_id, doc = entry
        else:
            doc = entry if isinstance(entry, dict) else {}
            module_id = _module_id_from_doc(doc)
        normalized.append((module_id, doc))
        if not isinstance(doc, dict) or module_id == "":
            continue
        body = doc.get("body")
        if not isinstance(body, list):
            continue
        for stmt in body:
            if isinstance(stmt, dict):
                _collect_sig(stmt, sigs, module_id, "")

    if len(sigs) == 0:
        return

    # Expand defaults in all modules
    for module_id, doc in normalized:
        if isinstance(doc, dict):
            import_modules, import_symbols = collect_import_maps(doc)
            _expand_walk(
                doc,
                sigs,
                current_module_id=module_id,
                import_modules=import_modules,
                import_symbols=import_symbols,
            )
