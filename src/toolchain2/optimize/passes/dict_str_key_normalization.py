"""Normalize dict[str, V] key nodes to avoid redundant string casts."""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result


def _norm_text(value: JsonVal) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _dict_key_type(owner_type: JsonVal) -> str:
    owner_t = _norm_text(owner_type)
    if not owner_t.startswith("dict[") or not owner_t.endswith("]"):
        return ""
    inner = owner_t[5 : len(owner_t) - 1].strip()
    if inner == "":
        return ""
    depth = 0
    split_at = -1
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch == "[" or ch == "<":
            depth += 1
        elif ch == "]" or ch == ">":
            if depth > 0:
                depth -= 1
        elif ch == "," and depth == 0:
            split_at = i
            break
        i += 1
    if split_at < 0:
        return ""
    key_t = inner[:split_at].strip()
    return _norm_text(key_t)


class DictStrKeyNormalizationPass(East3OptimizerPass):
    """Annotate dict-string key nodes with normalized key type metadata."""

    name: str = "DictStrKeyNormalizationPass"
    min_opt_level: int = 1

    def _mark_key(self, key_node: JsonVal) -> int:
        key = key_node if isinstance(key_node, dict) else None
        if key is None:
            return 0
        changed = 0
        key_t = _norm_text(key.get("resolved_type"))
        if key_t == "" or key_t == "unknown":
            key["resolved_type"] = "str"
            changed += 1
        if not bool(key.get("dict_key_verified", False)):
            key["dict_key_verified"] = True
            changed += 1
        return changed

    def _visit(self, node: JsonVal) -> int:
        changed = 0
        if isinstance(node, list):
            for item in node:
                changed += self._visit(item)
            return changed
        if not isinstance(node, dict):
            return 0

        kind = _norm_text(node.get("kind"))
        if kind == "Subscript":
            owner = node.get("value")
            owner_node: dict[str, JsonVal] | None = None
            if isinstance(owner, dict):
                owner_node = owner
            if owner_node is not None and _dict_key_type(owner_node.get("resolved_type")) == "str":
                changed += self._mark_key(node.get("slice"))
        elif kind == "DictGetMaybe" or kind == "DictGetDefault" or kind == "DictPop" or kind == "DictPopDefault":
            owner = node.get("owner")
            owner_node = None
            if isinstance(owner, dict):
                owner_node = owner
            if owner_node is not None and _dict_key_type(owner_node.get("resolved_type")) == "str":
                changed += self._mark_key(node.get("key"))
        elif kind == "Call":
            runtime_call = _norm_text(node.get("runtime_call"))
            if runtime_call == "dict.get" or runtime_call == "dict.pop":
                func_obj = node.get("func")
                if isinstance(func_obj, dict):
                    owner_obj = func_obj.get("value")
                    if isinstance(owner_obj, dict) and _dict_key_type(owner_obj.get("resolved_type")) == "str":
                        args_obj = node.get("args")
                        args = args_obj if isinstance(args_obj, list) else []
                        if len(args) >= 1:
                            changed += self._mark_key(args[0])

        for value in node.values():
            changed += self._visit(value)
        return changed

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        _ = context
        change_count = self._visit(east3_doc)
        warnings: list[str] = []
        return make_pass_result(change_count > 0, change_count, warnings, 0.0)
