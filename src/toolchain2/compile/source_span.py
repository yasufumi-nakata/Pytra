"""Source span normalization for EAST2 → EAST3.

Renames col → col_offset, end_col → end_col_offset.
Removes Module-level source_span (which has null fields).

§5.1: Any/object 禁止。
"""

from __future__ import annotations

from toolchain2.compile.jv import JsonVal, Node, jv_is_dict, jv_is_list
from toolchain2.common.kinds import MODULE


def normalize_source_span(span: JsonVal) -> JsonVal:
    """Rename col → col_offset, end_col → end_col_offset in a source_span."""
    if not isinstance(span, dict):
        return span
    d: Node = span
    out: Node = {}
    for k, v in d.items():
        if k == "col":
            out["col_offset"] = v
        elif k == "end_col":
            out["end_col_offset"] = v
        elif k == "col_offset" or k == "end_col_offset":
            out[k] = v
        else:
            out[k] = v
    return out


def walk_normalize_spans(node: JsonVal) -> JsonVal:
    """Recursively rename source_span fields and remove Module source_span."""
    if isinstance(node, list):
        result: list[JsonVal] = []
        for item in node:
            result.append(walk_normalize_spans(item))
        return result
    if not isinstance(node, dict):
        return node
    d: Node = node
    kind = d.get("kind", "")
    out: Node = {}
    for k, v in d.items():
        if k == "source_span":
            if kind == MODULE:
                # Remove Module-level source_span
                continue
            out[k] = normalize_source_span(v)
        else:
            out[k] = walk_normalize_spans(v)
    return out
