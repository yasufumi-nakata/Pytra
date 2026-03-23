"""EAST3 enumerate lowering pass.

Converts ``for i, v in enumerate(xs)`` into a counter-based loop:

    __enum_idx = 0
    for v in xs:
        i = __enum_idx
        ...body...
        __enum_idx += 1
"""

from __future__ import annotations

import copy
from typing import Any


_enum_counter: list[int] = [0]


def _next_enum_name() -> str:
    _enum_counter[0] += 1
    return "__enum_idx_" + str(_enum_counter[0])


def _safe_str(v: Any) -> str:
    if isinstance(v, str):
        return v.strip()
    return ""


def _lower_enumerate_in_stmts(stmts: list[Any]) -> list[Any]:
    """Walk statement list and expand enumerate ForCore loops."""
    result: list[Any] = []
    for stmt in stmts:
        if not isinstance(stmt, dict):
            result.append(stmt)
            continue
        kind = stmt.get("kind", "")

        if kind == "ForCore":
            expanded = _try_lower_enumerate_forcore(stmt)
            if expanded is not None:
                result.extend(expanded)
                continue

        # Recurse into nested blocks
        for key in ("body", "orelse"):
            nested = stmt.get(key)
            if isinstance(nested, list):
                stmt[key] = _lower_enumerate_in_stmts(nested)

        result.append(stmt)
    return result


def _try_lower_enumerate_forcore(stmt: dict[str, Any]) -> list[dict[str, Any]] | None:
    """If ForCore uses enumerate, return expanded statement list."""
    iter_plan = stmt.get("iter_plan")
    if not isinstance(iter_plan, dict):
        return None
    if iter_plan.get("kind") != "RuntimeIterForPlan":
        return None
    iter_expr = iter_plan.get("iter_expr")
    if not isinstance(iter_expr, dict):
        return None

    # Check for enumerate semantic tag or call
    semantic_tag = _safe_str(iter_expr.get("semantic_tag"))
    is_enumerate = semantic_tag == "iter.enumerate"
    if not is_enumerate:
        func = iter_expr.get("func")
        if isinstance(func, dict):
            is_enumerate = func.get("id") == "enumerate" or func.get("attr") == "enumerate"
    if not is_enumerate:
        return None

    # Extract enumerate arguments
    args = iter_expr.get("args", [])
    if not isinstance(args, list) or len(args) < 1:
        return None
    iterable = args[0]
    start_val = 0
    if len(args) >= 2:
        start_arg = args[1]
        if isinstance(start_arg, dict) and start_arg.get("kind") == "Constant":
            sv = start_arg.get("value")
            if isinstance(sv, int):
                start_val = sv

    # Get the target_plan — should be NameTarget (TupleTarget already expanded by P0-31)
    target_plan = stmt.get("target_plan", {})
    if not isinstance(target_plan, dict):
        return None

    # Find the index and value variable names from body assignments
    # P0-31 inserts: i = __iter_tmp[0], v = __iter_tmp[1]
    body = stmt.get("body", [])
    if not isinstance(body, list):
        return None

    idx_name = ""
    val_name = ""
    remaining_body: list[dict[str, Any]] = []
    iter_tmp = _safe_str(target_plan.get("id"))

    for i, s in enumerate(body):
        if not isinstance(s, dict):
            remaining_body.append(s)
            continue
        if s.get("kind") == "Assign":
            target = s.get("target")
            value = s.get("value")
            if isinstance(target, dict) and isinstance(value, dict):
                if value.get("kind") == "Subscript":
                    slice_val = value.get("slice", {})
                    if isinstance(slice_val, dict) and slice_val.get("kind") == "Constant":
                        idx = slice_val.get("value")
                        owner = value.get("value", {})
                        if isinstance(owner, dict) and _safe_str(owner.get("id")) == iter_tmp:
                            name = _safe_str(target.get("id"))
                            if idx == 0 and name != "":
                                idx_name = name
                                continue
                            elif idx == 1 and name != "":
                                val_name = name
                                continue
        remaining_body.append(s)

    if idx_name == "" or val_name == "":
        return None

    # Build expanded statements
    counter_name = _next_enum_name()

    # 1. Initialize counter
    init_counter: dict[str, Any] = {
        "kind": "Assign",
        "target": {"kind": "Name", "id": counter_name, "resolved_type": "int64"},
        "value": {"kind": "Constant", "value": start_val, "resolved_type": "int64"},
        "decl_type": "int64",
    }

    # 2. Build for loop over iterable (without enumerate)
    # Derive val_name's type from the tuple's second element
    # e.g. tuple[int64, int64] → int64 for the value variable
    raw_target_type = _safe_str(target_plan.get("target_type"))
    val_target_type = raw_target_type
    if raw_target_type.startswith("tuple[") and raw_target_type.endswith("]"):
        inner = raw_target_type[6:-1]
        parts: list[str] = []
        depth = 0
        cur = ""
        for ch in inner:
            if ch == "[":
                depth += 1
                cur += ch
            elif ch == "]":
                if depth > 0:
                    depth -= 1
                cur += ch
            elif ch == "," and depth == 0:
                parts.append(cur.strip())
                cur = ""
            else:
                cur += ch
        tail = cur.strip()
        if tail != "":
            parts.append(tail)
        if len(parts) >= 2:
            val_target_type = parts[1]
    new_target_plan: dict[str, Any] = {
        "kind": "NameTarget",
        "id": val_name,
        "target_type": val_target_type,
    }

    # New iter_plan: iterate over the original iterable
    new_iter_plan: dict[str, Any] = {
        "kind": "RuntimeIterForPlan",
        "iter_expr": copy.deepcopy(iterable),
        "dispatch_mode": iter_plan.get("dispatch_mode", "native"),
        "init_op": "ObjIterInit",
        "next_op": "ObjIterNext",
    }

    # Body: assign counter to idx_name, then original body, then increment
    assign_idx: dict[str, Any] = {
        "kind": "Assign",
        "target": {"kind": "Name", "id": idx_name, "resolved_type": "int64"},
        "value": {"kind": "Name", "id": counter_name, "resolved_type": "int64"},
        "decl_type": "int64",
    }
    increment: dict[str, Any] = {
        "kind": "AugAssign",
        "target": {"kind": "Name", "id": counter_name, "resolved_type": "int64"},
        "op": "Add",
        "value": {"kind": "Constant", "value": 1, "resolved_type": "int64"},
    }

    new_body = [assign_idx] + remaining_body + [increment]

    new_forcore: dict[str, Any] = {
        "kind": "ForCore",
        "iter_mode": stmt.get("iter_mode", "runtime_protocol"),
        "iter_plan": new_iter_plan,
        "target_plan": new_target_plan,
        "body": new_body,
        "orelse": stmt.get("orelse", []),
    }

    return [init_counter, new_forcore]


def lower_enumerate(module: dict[str, Any]) -> dict[str, Any]:
    """Top-level entry: lower enumerate loops in an EAST3 Module."""
    _enum_counter[0] = 0
    body = module.get("body")
    if isinstance(body, list):
        module["body"] = _lower_enumerate_in_stmts(body)
    return module
