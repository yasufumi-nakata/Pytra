"""Post-processing: normalize JSON field ordering to match golden files.

The golden east2 files have a specific field ordering convention.
This module reorders fields to match.

§5 準拠: Any/object 禁止、pytra.std.* のみ使用。
"""

from __future__ import annotations

from pytra.std.json import JsonVal
from pytra.std import json


def _jv_obj(value: JsonVal) -> dict[str, JsonVal]:
    obj = json.JsonValue(value).as_obj()
    if obj is None:
        empty: dict[str, JsonVal] = {}
        return empty
    return obj.raw


def _jv_arr(value: JsonVal) -> list[JsonVal]:
    arr = json.JsonValue(value).as_arr()
    if arr is None:
        empty: list[JsonVal] = []
        return empty
    return arr.raw


def _jv_str(value: JsonVal) -> str:
    raw = json.JsonValue(value).as_str()
    if raw is None:
        return ""
    return "" + raw


def _dict_get_str(obj: dict[str, JsonVal], key: str) -> str:
    if key not in obj:
        return ""
    return _jv_str(obj[key])


def _fields_csv(csv_text: str) -> list[str]:
    parts: list[str] = []
    for raw_part in csv_text.split(","):
        part = raw_part.strip()
        if part != "":
            parts.append(part)
    return parts


# Expression node field order: resolved_type comes right after source_span
_EXPR_FIELD_ORDER: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr")

# Name-specific trailing fields
_NAME_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, id, type_expr")

# Constant-specific trailing fields
_CONSTANT_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, value")

# BinOp
_BINOP_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, left, op, right")

# UnaryOp
_UNARYOP_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, op, operand")

# Compare
_COMPARE_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, left, ops, comparators")

# Call
_CALL_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, func, args, keywords, lowered_kind, builtin_name, runtime_call, resolved_runtime_call, resolved_runtime_source, runtime_module_id, runtime_symbol, runtime_call_adapter_kind, semantic_tag, runtime_owner")

# Attribute
_ATTRIBUTE_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, value, attr")

# Subscript
_SUBSCRIPT_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, value, slice, lowered_kind, lower, upper, step")

# List
_LIST_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, elements")

# Dict
_DICT_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, keys, values")

# Set
_SET_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, elements")

# Tuple
_TUPLE_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, elements")

# IfExp
_IFEXP_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, test, body, orelse")

# BoolOp
_BOOLOP_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, op, values")

# ListComp
_LISTCOMP_FIELDS: list[str] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, elt, generators")

# FunctionDef
_FUNCDEF_FIELDS: list[str] = _fields_csv("kind, source_span, name, original_name, arg_types, arg_order, arg_defaults, arg_index, return_type, arg_usage, renamed_symbols, docstring, body, is_generator, yield_value_type, arg_type_exprs, return_type_expr, leading_comments, leading_trivia")

_CLOSUREDEF_FIELDS: list[str] = _fields_csv("kind, source_span, name, original_name, captures, capture_types, capture_modes, is_recursive, arg_types, arg_order, arg_defaults, arg_index, return_type, arg_usage, renamed_symbols, docstring, body, is_generator, yield_value_type, arg_type_exprs, return_type_expr, leading_comments, leading_trivia")

# ClassDef
_CLASSDEF_FIELDS: list[str] = _fields_csv("kind, source_span, name, original_name, base, dataclass, field_types, bases, decorators, body, class_storage_hint, leading_comments, leading_trivia")

# ForRange
_FORRANGE_FIELDS: list[str] = _fields_csv("kind, source_span, target, target_type, start, stop, step, range_mode, body, orelse")

# Assign
_ASSIGN_FIELDS: list[str] = _fields_csv("kind, source_span, target, targets, value, declare, decl_type, declare_init")

# AnnAssign
_ANNASSIGN_FIELDS: list[str] = _fields_csv("kind, source_span, target, annotation, value, declare, decl_type, annotation_type_expr, decl_type_expr, simple")

# AugAssign
_AUGASSIGN_FIELDS: list[str] = _fields_csv("kind, source_span, target, op, value, declare, decl_type")

# Import resolution section
_IMPORT_RESOLUTION_FIELDS: list[str] = _fields_csv("schema_version, bindings, qualified_refs")

# Meta section
_META_FIELDS: list[str] = _fields_csv("parser_backend, import_resolution, import_bindings, qualified_symbol_refs, import_modules, import_symbols, dispatch_mode")

# Module
_MODULE_FIELDS: list[str] = _fields_csv("kind, source_path, source_span, body, main_guard_body, renamed_symbols, meta, east_stage, schema_version")


def _build_kind_fields() -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    fields["Name"] = _NAME_FIELDS
    fields["Constant"] = _CONSTANT_FIELDS
    fields["BinOp"] = _BINOP_FIELDS
    fields["UnaryOp"] = _UNARYOP_FIELDS
    fields["Compare"] = _COMPARE_FIELDS
    fields["Call"] = _CALL_FIELDS
    fields["Attribute"] = _ATTRIBUTE_FIELDS
    fields["Subscript"] = _SUBSCRIPT_FIELDS
    fields["List"] = _LIST_FIELDS
    fields["Dict"] = _DICT_FIELDS
    fields["Set"] = _SET_FIELDS
    fields["Tuple"] = _TUPLE_FIELDS
    fields["IfExp"] = _IFEXP_FIELDS
    fields["BoolOp"] = _BOOLOP_FIELDS
    fields["ListComp"] = _LISTCOMP_FIELDS
    fields["FunctionDef"] = _FUNCDEF_FIELDS
    fields["ClosureDef"] = _CLOSUREDEF_FIELDS
    fields["ClassDef"] = _CLASSDEF_FIELDS
    fields["For"] = _fields_csv("kind, source_span, target, target_type, iter_mode, iter_source_type, iter_element_type, iter, body, orelse")
    fields["RangeExpr"] = _fields_csv("kind, source_span, resolved_type, casts, borrow_kind, repr, start, stop, step, range_mode")
    fields["ForRange"] = _FORRANGE_FIELDS
    fields["Assign"] = _ASSIGN_FIELDS
    fields["AnnAssign"] = _ANNASSIGN_FIELDS
    fields["AugAssign"] = _AUGASSIGN_FIELDS
    fields["Module"] = _MODULE_FIELDS
    return fields


_KIND_FIELDS: dict[str, list[str]] = _build_kind_fields()

def normalize_field_order(doc: JsonVal, parent_key: str = "") -> JsonVal:
    """Recursively normalize field ordering in a JSON document."""
    obj = _jv_obj(doc)
    if len(obj) > 0:
        kind: str = _dict_get_str(obj, "kind")
        ordered: dict[str, JsonVal]
        if kind != "" and kind in _KIND_FIELDS:
            ordered = _reorder_dict(obj, _KIND_FIELDS[kind])
        elif parent_key == "meta":
            ordered = _reorder_dict(obj, _META_FIELDS)
        elif parent_key == "import_resolution":
            ordered = _reorder_dict(obj, _IMPORT_RESOLUTION_FIELDS)
        else:
            ordered = obj
        result: dict[str, JsonVal] = {}
        for k, v in ordered.items():
            result[k] = normalize_field_order(v, parent_key=k)
        return result
    arr = _jv_arr(doc)
    if len(arr) > 0:
        out: list[JsonVal] = []
        for item in arr:
            out.append(normalize_field_order(item, parent_key=parent_key))
        return out
    return doc


def _reorder_dict(d: dict[str, JsonVal], field_order: list[str]) -> dict[str, JsonVal]:
    """Reorder dict keys according to field_order, preserving extra keys at end."""
    out: dict[str, JsonVal] = {}
    # Add fields in specified order
    for key in field_order:
        if key in d:
            out[key] = d[key]
    # Add remaining fields not in the specified order
    for key in d:
        if key not in out:
            out[key] = d[key]
    return out
