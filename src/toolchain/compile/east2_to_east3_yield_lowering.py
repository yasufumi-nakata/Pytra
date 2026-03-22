"""EAST3 yield lowering: convert generator functions to list accumulation.

Transforms generator functions (containing ``yield``) into regular functions
that accumulate yielded values into a list and return it.  This is the
simplest generator lowering strategy and works for all target languages.

Before:
    def gen(n: int) -> int:
        i = 0
        while i < n:
            yield i
            i += 1

After:
    def gen(n: int) -> list[int]:
        __yield_values: list[int] = []
        i = 0
        while i < n:
            __yield_values.append(i)
            i += 1
        return __yield_values
"""

from __future__ import annotations

import copy
from typing import Any


def _contains_yield(node: Any) -> bool:
    """Check if *node* contains any Yield statement."""
    if isinstance(node, dict):
        if node.get("kind") == "Yield":
            return True
        for v in node.values():
            if _contains_yield(v):
                return True
    elif isinstance(node, list):
        for item in node:
            if _contains_yield(item):
                return True
    return False


def _replace_yield_with_append(node: Any, accumulator_name: str) -> Any:
    """Replace Yield nodes with list.append() calls."""
    if isinstance(node, list):
        result: list[Any] = []
        for item in node:
            replaced = _replace_yield_with_append(item, accumulator_name)
            if isinstance(replaced, list):
                result.extend(replaced)
            else:
                result.append(replaced)
        return result
    if not isinstance(node, dict):
        return node
    nd: dict[str, Any] = node
    kind = nd.get("kind", "")

    if kind == "Yield":
        # yield value → __yield_values.append(value)
        value = nd.get("value")
        if value is None:
            value = {"kind": "Constant", "value": None, "resolved_type": "None"}
        append_call: dict[str, Any] = {
            "kind": "Expr",
            "value": {
                "kind": "Call",
                "func": {
                    "kind": "Attribute",
                    "value": {"kind": "Name", "id": accumulator_name, "resolved_type": "list[object]"},
                    "attr": "append",
                },
                "args": [value],
                "resolved_type": "None",
            },
        }
        span = nd.get("source_span")
        if isinstance(span, dict):
            append_call["source_span"] = span
        return append_call

    # Recurse into children
    out: dict[str, Any] = {}
    for key, val in nd.items():
        if key == "body" or key == "orelse" or key == "finalbody":
            out[key] = _replace_yield_with_append(val, accumulator_name)
        elif key == "handlers" and isinstance(val, list):
            handlers: list[Any] = []
            for h in val:
                if isinstance(h, dict):
                    new_h = dict(h)
                    if "body" in new_h:
                        new_h["body"] = _replace_yield_with_append(new_h["body"], accumulator_name)
                    handlers.append(new_h)
                else:
                    handlers.append(h)
            out[key] = handlers
        else:
            out[key] = val
    return out


def _lower_generator_function(func: dict[str, Any]) -> None:
    """Transform a generator FunctionDef into list accumulation in place."""
    body = func.get("body")
    if not isinstance(body, list):
        return

    # Determine yield element type from return_type
    ret_type = func.get("return_type", "")
    if isinstance(ret_type, str):
        ret_type = ret_type.strip()
    else:
        ret_type = ""
    elem_type = "object"
    if ret_type.startswith("list[") and ret_type.endswith("]"):
        elem_type = ret_type[5:-1]
    elif ret_type not in ("", "unknown"):
        elem_type = ret_type
        func["return_type"] = "list[" + ret_type + "]"

    accumulator_name = "__yield_values"
    list_type = "list[" + elem_type + "]"

    # Insert accumulator declaration at the beginning of the body
    init_stmt: dict[str, Any] = {
        "kind": "AnnAssign",
        "target": {
            "kind": "Name",
            "id": accumulator_name,
            "resolved_type": list_type,
        },
        "annotation": list_type,
        "decl_type": list_type,
        "declare": True,
        "value": {
            "kind": "List",
            "elements": [],
            "resolved_type": list_type,
        },
    }

    # Replace all Yield with append
    new_body = _replace_yield_with_append(body, accumulator_name)
    if not isinstance(new_body, list):
        new_body = body

    # Append return statement at the end
    return_stmt: dict[str, Any] = {
        "kind": "Return",
        "value": {
            "kind": "Name",
            "id": accumulator_name,
            "resolved_type": list_type,
        },
    }

    func["body"] = [init_stmt] + new_body + [return_stmt]


def lower_yield_generators(module: dict[str, Any]) -> dict[str, Any]:
    """Walk module and lower all generator functions to list accumulation.

    Mutates *module* in place and returns it.
    """
    _walk_and_lower(module)
    return module


def _walk_and_lower(node: Any) -> None:
    if isinstance(node, list):
        for item in node:
            _walk_and_lower(item)
        return
    if not isinstance(node, dict):
        return
    nd: dict[str, Any] = node
    kind = nd.get("kind", "")

    if kind == "FunctionDef":
        body = nd.get("body")
        if isinstance(body, list) and _contains_yield(body):
            _lower_generator_function(nd)
        # Recurse into body for nested functions
        body = nd.get("body")
        if isinstance(body, list):
            for stmt in body:
                _walk_and_lower(stmt)
        return

    if kind in ("ClassDef", "Module"):
        body = nd.get("body")
        if isinstance(body, list):
            for stmt in body:
                _walk_and_lower(stmt)
        return

    for val in nd.values():
        if isinstance(val, (dict, list)):
            _walk_and_lower(val)
