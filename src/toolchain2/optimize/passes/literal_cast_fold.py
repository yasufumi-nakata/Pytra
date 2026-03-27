"""Fold literal static_cast calls when conversion is provably no-op."""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result


def _normalize_type_name(value: JsonVal) -> str:
    if isinstance(value, str):
        text = value.strip()
        if text != "":
            return text
    return "unknown"


def _copy_node(node: dict[str, JsonVal]) -> dict[str, JsonVal]:
    out: dict[str, JsonVal] = {}
    for key, value in node.items():
        out[key] = value
    return out


def _try_fold_literal_static_cast(call_node: dict[str, JsonVal]) -> tuple[bool, dict[str, JsonVal]]:
    if call_node.get("kind") != "Call":
        return False, {}
    if call_node.get("lowered_kind") != "BuiltinCall":
        return False, {}
    if call_node.get("runtime_call") != "static_cast":
        return False, {}

    args_obj = call_node.get("args")
    args = args_obj if isinstance(args_obj, list) else []
    if len(args) != 1:
        return False, {}
    arg = args[0]
    if not isinstance(arg, dict):
        return False, {}
    if arg.get("kind") != "Constant":
        return False, {}

    target_t = _normalize_type_name(call_node.get("resolved_type"))
    source_t = _normalize_type_name(arg.get("resolved_type"))
    if target_t == "unknown" or source_t == "unknown":
        return False, {}
    if target_t != source_t:
        return False, {}

    folded = _copy_node(arg)
    span_obj = call_node.get("source_span")
    if isinstance(span_obj, dict):
        folded["source_span"] = span_obj
    repr_obj = call_node.get("repr")
    if isinstance(repr_obj, str) and repr_obj != "":
        folded["repr"] = repr_obj
    return True, folded


class LiteralCastFoldPass(East3OptimizerPass):
    """Fold literal casts conservatively under fail-closed guards."""

    name: str = "LiteralCastFoldPass"
    min_opt_level: int = 1

    def _rewrite(self, node: JsonVal) -> tuple[JsonVal, int]:
        if isinstance(node, list):
            out_list: list[JsonVal] = list(node)
            changed = 0
            for i, item in enumerate(node):
                new_item, delta = self._rewrite(item)
                if new_item is not item:
                    out_list[i] = new_item
                changed += delta
            return out_list, changed

        if not isinstance(node, dict):
            return node, 0

        out_dict = _copy_node(node)
        changed = 0
        keys = list(node.keys())
        for key in keys:
            value = node[key]
            new_value, delta = self._rewrite(value)
            if new_value is not value:
                out_dict[key] = new_value
            changed += delta

        did_fold, folded = _try_fold_literal_static_cast(out_dict)
        if did_fold:
            return folded, changed + 1
        return out_dict, changed

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        _ = context
        _, change_count = self._rewrite(east3_doc)
        warnings: list[str] = []
        return make_pass_result(change_count > 0, change_count, warnings, 0.0)
