"""Fold IsInstance checks on statically-known POD types to boolean constants.

When the value's resolved_type is a concrete POD type and the expected_type_name
is also a POD type, the result is provably True (exact match) or False (mismatch).
This is constant-folding responsibility of the optimizer, not the emitter.

Uses in-place mutation of parent containers (same pattern as
RangeForCanonicalizationPass) so changes are visible to the PassManager.
"""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result

# Concrete scalar types whose identity is determined purely by name.
# Union types, 'any', 'object', 'int', 'float' etc. are intentionally excluded.
_POD_TYPES: frozenset[str] = frozenset({
    "int8", "int16", "int32", "int64",
    "uint8", "uint16", "uint32", "uint64",
    "float32", "float64",
    "bool",
})


def _make_bool_const(value: bool, span: JsonVal, repr_str: str) -> dict[str, JsonVal]:
    node: dict[str, JsonVal] = {
        "kind": "Constant",
        "resolved_type": "bool",
        "borrow_kind": "value",
        "casts": [],
        "value": value,
        "repr": repr_str,
    }
    if isinstance(span, dict):
        node["source_span"] = span
    return node


def _try_fold(node: dict[str, JsonVal]) -> tuple[bool, dict[str, JsonVal]]:
    if node.get("kind") != "IsInstance":
        return False, {}

    expected = node.get("expected_type_name")
    if not isinstance(expected, str) or expected not in _POD_TYPES:
        return False, {}

    value_node = node.get("value")
    if not isinstance(value_node, dict):
        return False, {}

    val_type = value_node.get("resolved_type")
    if not isinstance(val_type, str) or val_type not in _POD_TYPES:
        return False, {}

    result = val_type == expected
    repr_str = node.get("repr")
    if not isinstance(repr_str, str):
        repr_str = str(result)
    return True, _make_bool_const(result, node.get("source_span"), repr_str)


def _visit(node: JsonVal) -> int:
    """In-place visitor: replace IsInstance children in lists and dicts."""
    changed = 0
    if isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, dict):
                did_fold, folded = _try_fold(item)
                if did_fold:
                    node[i] = folded
                    changed += 1
                    continue
            changed += _visit(item)
        return changed
    if isinstance(node, dict):
        for key in list(node.keys()):
            value = node[key]
            if isinstance(value, dict):
                did_fold, folded = _try_fold(value)
                if did_fold:
                    node[key] = folded
                    changed += 1
                    continue
            changed += _visit(value)
    return changed


class PodIsinstanceFoldPass(East3OptimizerPass):
    """Fold IsInstance on POD types to Constant(bool) nodes."""

    name: str = "PodIsinstanceFoldPass"
    min_opt_level: int = 1

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        _ = context
        change_count = _visit(east3_doc)
        return make_pass_result(change_count > 0, change_count, [], 0.0)
