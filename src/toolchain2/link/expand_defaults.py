"""Cross-module default argument expansion for linked programs.

Link 段で全 module の FunctionDef から arg_defaults を収集し、
Call ノードの引数が不足している場合にデフォルト値を補完する。

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.common.jv import deep_copy_json


def _collect_all_fn_sigs(modules: list[dict[str, JsonVal]]) -> dict[str, dict[str, JsonVal]]:
    """Collect function signatures from all modules.

    Returns: {fn_name: {"arg_order": [...], "arg_defaults": {...}}}
    Also keyed by qualified name: module_id::fn_name
    """
    sigs: dict[str, dict[str, JsonVal]] = {}
    for doc in modules:
        if not isinstance(doc, dict):
            continue
        module_id = ""
        meta = doc.get("meta")
        if isinstance(meta, dict):
            lp = meta.get("linked_program_v1")
            if isinstance(lp, dict):
                mid = lp.get("module_id")
                if isinstance(mid, str):
                    module_id = mid

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
        ao = node.get("arg_order")
        ad = node.get("arg_defaults")
        if not isinstance(ao, list):
            return
        sig: dict[str, JsonVal] = {
            "arg_order": ao,
            "arg_defaults": ad if isinstance(ad, dict) else {},
        }
        # Register by bare name and qualified name
        full = class_name + "." + name if class_name != "" else name
        sigs[name] = sig
        if full != name:
            sigs[full] = sig
        if module_id != "":
            sigs[module_id + "::" + name] = sig
            if full != name:
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


def _expand_walk(node: JsonVal, sigs: dict[str, dict[str, JsonVal]]) -> None:
    """Recursively walk the AST and expand default arguments in Call nodes."""
    if isinstance(node, list):
        for item in node:
            _expand_walk(item, sigs)
        return
    if not isinstance(node, dict):
        return

    if node.get("kind") == "Call":
        func = node.get("func")
        call_name = ""
        if isinstance(func, dict):
            fk = func.get("kind")
            if fk == "Name":
                fn_id = func.get("id")
                if isinstance(fn_id, str):
                    call_name = fn_id
            elif fk == "Attribute":
                attr = func.get("attr")
                if isinstance(attr, str):
                    call_name = attr

        if call_name != "" and call_name in sigs:
            sig = sigs[call_name]
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

    for v in node.values():
        if isinstance(v, (dict, list)):
            _expand_walk(v, sigs)


def expand_cross_module_defaults(linked_modules: list[dict[str, JsonVal]]) -> None:
    """Expand default arguments in Call nodes across all linked modules.

    Mutates the east_doc of each module in-place.
    """
    # Collect signatures from all modules
    sigs = _collect_all_fn_sigs(linked_modules)
    if len(sigs) == 0:
        return

    # Expand defaults in all modules
    for doc in linked_modules:
        if isinstance(doc, dict):
            _expand_walk(doc, sigs)
