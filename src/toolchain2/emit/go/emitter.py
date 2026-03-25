"""EAST3 → Go source code emitter.

お手本 emitter: 他言語 emitter のテンプレートとなる設計。
入力は linked EAST3 JSON (dict) のみ。toolchain/ への依存なし。

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from pytra.std.json import JsonVal

from toolchain2.emit.go.types import go_type, go_zero_value, _safe_go_ident


# ---------------------------------------------------------------------------
# Emit context (mutable state for one module emission)
# ---------------------------------------------------------------------------

@dataclass
class EmitContext:
    """Per-module mutable state during emission."""
    module_id: str = ""
    is_entry: bool = False
    indent_level: int = 0
    lines: list[str] = field(default_factory=list)
    imports_needed: set[str] = field(default_factory=set)
    # Variable types in current scope
    var_types: dict[str, str] = field(default_factory=dict)
    # Class info
    class_names: set[str] = field(default_factory=set)
    class_bases: dict[str, str] = field(default_factory=dict)
    # Current class context (for method emission)
    current_class: str = ""
    current_receiver: str = "self"


# ---------------------------------------------------------------------------
# Indentation helpers
# ---------------------------------------------------------------------------

def _indent(ctx: EmitContext) -> str:
    return "\t" * ctx.indent_level


def _emit(ctx: EmitContext, line: str) -> None:
    ctx.lines.append(_indent(ctx) + line)


def _emit_raw(ctx: EmitContext, line: str) -> None:
    ctx.lines.append(line)


def _emit_blank(ctx: EmitContext) -> None:
    ctx.lines.append("")


# ---------------------------------------------------------------------------
# Node accessors (safe typed access to EAST3 JSON)
# ---------------------------------------------------------------------------

def _str(node: dict[str, JsonVal], key: str) -> str:
    v = node.get(key)
    return v if isinstance(v, str) else ""


def _int(node: dict[str, JsonVal], key: str) -> int:
    v = node.get(key)
    return v if isinstance(v, int) else 0


def _bool(node: dict[str, JsonVal], key: str) -> bool:
    v = node.get(key)
    return v if isinstance(v, bool) else False


def _list(node: dict[str, JsonVal], key: str) -> list[JsonVal]:
    v = node.get(key)
    return v if isinstance(v, list) else []


def _dict(node: dict[str, JsonVal], key: str) -> dict[str, JsonVal]:
    v = node.get(key)
    return v if isinstance(v, dict) else {}


# ---------------------------------------------------------------------------
# Expression emission
# ---------------------------------------------------------------------------

def _emit_expr(ctx: EmitContext, node: JsonVal) -> str:
    """Emit an expression node and return Go code string."""
    if not isinstance(node, dict):
        return "nil"

    kind = _str(node, "kind")

    if kind == "Constant":
        return _emit_constant(ctx, node)
    if kind == "Name":
        return _emit_name(ctx, node)
    if kind == "BinOp":
        return _emit_binop(ctx, node)
    if kind == "UnaryOp":
        return _emit_unaryop(ctx, node)
    if kind == "Compare":
        return _emit_compare(ctx, node)
    if kind == "BoolOp":
        return _emit_boolop(ctx, node)
    if kind == "Call":
        return _emit_call(ctx, node)
    if kind == "Attribute":
        return _emit_attribute(ctx, node)
    if kind == "Subscript":
        return _emit_subscript(ctx, node)
    if kind == "List":
        return _emit_list_literal(ctx, node)
    if kind == "Dict":
        return _emit_dict_literal(ctx, node)
    if kind == "Set":
        return _emit_set_literal(ctx, node)
    if kind == "Tuple":
        return _emit_tuple_literal(ctx, node)
    if kind == "IfExp":
        return _emit_ifexp(ctx, node)
    if kind == "JoinedStr":
        return _emit_fstring(ctx, node)
    if kind == "FormattedValue":
        return _emit_formatted_value(ctx, node)
    if kind == "Lambda":
        return _emit_lambda(ctx, node)
    if kind == "Slice":
        return _emit_slice_expr(ctx, node)
    if kind == "IsInstance":
        return _emit_isinstance(ctx, node)
    if kind == "Unbox":
        return _emit_expr(ctx, node.get("value"))
    if kind == "Box":
        return _emit_expr(ctx, node.get("value"))
    if kind == "ObjStr":
        arg = node.get("value")
        return "__pytra_str(" + _emit_expr(ctx, arg) + ")"
    if kind == "ObjLen":
        arg = node.get("value")
        return "__pytra_len(" + _emit_expr(ctx, arg) + ")"
    if kind == "ObjBool":
        arg = node.get("value")
        return "__pytra_bool(" + _emit_expr(ctx, arg) + ")"
    if kind == "ListComp":
        return _emit_list_comp(ctx, node)
    if kind == "SetComp":
        return _emit_set_comp(ctx, node)
    if kind == "DictComp":
        return _emit_dict_comp(ctx, node)

    return "nil /* unsupported expr: " + kind + " */"


def _emit_constant(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    val = node.get("value")
    rt = _str(node, "resolved_type")
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, int):
        if rt in ("float64", "float32", "float"):
            return str(float(val))
        return str(val)
    if isinstance(val, float):
        s = repr(val)
        if s == "inf":
            ctx.imports_needed.add("math")
            return "math.Inf(1)"
        if s == "-inf":
            ctx.imports_needed.add("math")
            return "math.Inf(-1)"
        return s
    if isinstance(val, str):
        # Go string literal
        return _go_string_literal(val)
    return repr(val)


def _go_string_literal(s: str) -> str:
    """Encode a string as a Go string literal."""
    out: list[str] = ['"']
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 32:
            out.append("\\x" + format(ord(ch), "02x"))
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _emit_name(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    name = _str(node, "id")
    if name == "":
        name = _str(node, "repr")
    if name == "True":
        return "true"
    if name == "False":
        return "false"
    if name == "None":
        return "nil"
    if name == "self" and ctx.current_receiver != "":
        return ctx.current_receiver
    # Go control flow keywords used as statements
    if name == "continue":
        return "continue"
    if name == "break":
        return "break"
    return _safe_go_ident(name)


def _emit_binop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    left = _emit_expr(ctx, node.get("left"))
    right = _emit_expr(ctx, node.get("right"))
    op = _str(node, "op")
    go_op = _BINOP_MAP.get(op, "+")
    rt = _str(node, "resolved_type")

    # Integer division
    if op == "Div" and rt in ("int64", "int32", "int", "int8", "int16", "uint8"):
        return "(" + left + " / " + right + ")"
    # Floor division
    if op == "FloorDiv":
        return "__pytra_floordiv(" + left + ", " + right + ")"
    # Power
    if op == "Pow":
        ctx.imports_needed.add("math")
        return "math.Pow(float64(" + left + "), float64(" + right + "))"

    return "(" + left + " " + go_op + " " + right + ")"


_BINOP_MAP: dict[str, str] = {
    "Add": "+", "Sub": "-", "Mult": "*", "Div": "/",
    "Mod": "%", "BitOr": "|", "BitAnd": "&", "BitXor": "^",
    "LShift": "<<", "RShift": ">>",
}


def _emit_unaryop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    operand = _emit_expr(ctx, node.get("operand"))
    op = _str(node, "op")
    if op == "USub":
        return "(-" + operand + ")"
    if op == "Not":
        return "(!" + operand + ")"
    if op == "Invert":
        return "(^" + operand + ")"
    return operand


def _emit_compare(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    left = _emit_expr(ctx, node.get("left"))
    ops = _list(node, "ops")
    comparators = _list(node, "comparators")
    if len(ops) == 0 or len(comparators) == 0:
        return left

    parts: list[str] = []
    prev = left
    for i in range(len(ops)):
        op_str = ops[i] if isinstance(ops[i], str) else ""
        comp_node = comparators[i] if i < len(comparators) else None
        right = _emit_expr(ctx, comp_node)

        if op_str == "In":
            parts.append("__pytra_contains(" + right + ", " + prev + ")")
        elif op_str == "NotIn":
            parts.append("!__pytra_contains(" + right + ", " + prev + ")")
        elif op_str == "Is":
            parts.append("(" + prev + " == " + right + ")")
        elif op_str == "IsNot":
            parts.append("(" + prev + " != " + right + ")")
        else:
            go_cmp = _COMPARE_MAP.get(op_str, "==")
            parts.append("(" + prev + " " + go_cmp + " " + right + ")")
        prev = right

    if len(parts) == 1:
        return parts[0]
    return "(" + " && ".join(parts) + ")"


# str methods that map to runtime helper functions
_STR_METHOD_HELPERS: dict[str, str] = {
    "isdigit": "__pytra_isdigit",
    "isalpha": "__pytra_isalpha",
    "isalnum": "__pytra_isalnum",
    "isspace": "__pytra_isspace",
    "strip": "__pytra_strip",
    "lstrip": "__pytra_lstrip",
    "rstrip": "__pytra_rstrip",
    "startswith": "__pytra_startswith",
    "endswith": "__pytra_endswith",
    "replace": "__pytra_replace",
    "find": "__pytra_find",
    "rfind": "__pytra_rfind",
    "split": "__pytra_split",
    "join": "__pytra_join",
    "upper": "__pytra_upper",
    "lower": "__pytra_lower",
    "append": "append",  # handled separately via list
}

_COMPARE_MAP: dict[str, str] = {
    "Eq": "==", "NotEq": "!=", "Lt": "<", "LtE": "<=",
    "Gt": ">", "GtE": ">=",
}


def _emit_boolop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    op = _str(node, "op")
    values = _list(node, "values")
    go_op = " && " if op == "And" else " || "
    parts = [_emit_expr(ctx, v) for v in values]
    return "(" + go_op.join(parts) + ")"


def _emit_call(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    lowered = _str(node, "lowered_kind")
    if lowered == "BuiltinCall":
        return _emit_builtin_call(ctx, node)

    func = node.get("func")
    args = _list(node, "args")
    arg_strs = [_emit_expr(ctx, a) for a in args]

    if isinstance(func, dict):
        func_kind = _str(func, "kind")
        if func_kind == "Attribute":
            owner = _emit_expr(ctx, func.get("value"))
            attr = _str(func, "attr")
            # str methods → runtime helper functions
            if attr in _STR_METHOD_HELPERS:
                return _STR_METHOD_HELPERS[attr] + "(" + owner + ", " + ", ".join(arg_strs) + ")" if len(arg_strs) > 0 else _STR_METHOD_HELPERS[attr] + "(" + owner + ")"
            # dict.get → __pytra_dict_get
            if attr == "get" and len(arg_strs) >= 1:
                owner_rt = _str(func.get("value", {}), "resolved_type") if isinstance(func.get("value"), dict) else ""
                if owner_rt.startswith("dict[") or owner_rt.startswith("map["):
                    if len(arg_strs) >= 2:
                        return "__pytra_dict_get(" + owner + ", " + arg_strs[0] + ", " + arg_strs[1] + ")"
                    return owner + "[" + arg_strs[0] + "]"
            return owner + "." + _safe_go_ident(attr) + "(" + ", ".join(arg_strs) + ")"
        if func_kind == "Name":
            fn_name = _str(func, "id")
            if fn_name == "":
                fn_name = _str(func, "repr")
            # Class constructor: ClassName(...) → NewClassName(...)
            if fn_name in ctx.class_names:
                return "New" + _safe_go_ident(fn_name) + "(" + ", ".join(arg_strs) + ")"
            return _safe_go_ident(fn_name) + "(" + ", ".join(arg_strs) + ")"

    fn = _emit_expr(ctx, func)
    return fn + "(" + ", ".join(arg_strs) + ")"


def _emit_builtin_call(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    rc = _str(node, "runtime_call")
    bn = _str(node, "builtin_name")
    args = _list(node, "args")
    arg_strs = [_emit_expr(ctx, a) for a in args]

    # Type cast builtins
    if rc == "static_cast":
        rt = _str(node, "resolved_type")
        gt = go_type(rt)
        # Check if source is string → int conversion (needs runtime helper)
        if len(args) >= 1 and isinstance(args[0], dict):
            src_type = _str(args[0], "resolved_type")
            if src_type == "str" and gt in ("int64", "int32"):
                return "__pytra_str_to_int64(" + arg_strs[0] + ")"
        if len(arg_strs) >= 1:
            return gt + "(" + arg_strs[0] + ")"
        return gt + "(0)"

    # py_to_string
    if rc == "py_to_string":
        if len(arg_strs) >= 1:
            return "__pytra_str(" + arg_strs[0] + ")"
        return "\"\""

    # print
    if rc == "py_print" or bn == "print":
        return "__pytra_print(" + ", ".join(arg_strs) + ")"

    # len
    if rc == "py_len" or bn == "len":
        if len(arg_strs) >= 1:
            return "__pytra_len(" + arg_strs[0] + ")"

    # Container constructors
    if rc == "bytearray_ctor" or rc == "bytes_ctor":
        if len(arg_strs) >= 1:
            return "[]byte(" + arg_strs[0] + ")"
        return "[]byte{}"

    if rc == "set_ctor":
        return "__pytra_set(" + ", ".join(arg_strs) + ")"

    # Container methods
    if rc == "list.append":
        func = node.get("func")
        if isinstance(func, dict):
            owner = _emit_expr(ctx, func.get("value"))
            if len(arg_strs) >= 1:
                return owner + " = append(" + owner + ", " + arg_strs[0] + ")"

    if rc == "set.add":
        func = node.get("func")
        if isinstance(func, dict):
            owner = _emit_expr(ctx, func.get("value"))
            if len(arg_strs) >= 1:
                return owner + "[" + arg_strs[0] + "] = struct{}{}"

    # enumerate / reversed
    if rc == "py_enumerate" or bn == "enumerate":
        return "__pytra_enumerate(" + ", ".join(arg_strs) + ")"
    if rc == "py_reversed" or bn == "reversed":
        return "__pytra_reversed(" + ", ".join(arg_strs) + ")"

    # abs / min / max / sum
    if bn == "abs" and len(arg_strs) >= 1:
        return "__pytra_abs(" + arg_strs[0] + ")"
    if bn == "min":
        return "__pytra_min(" + ", ".join(arg_strs) + ")"
    if bn == "max":
        return "__pytra_max(" + ", ".join(arg_strs) + ")"
    if bn == "sum" and len(arg_strs) >= 1:
        return "__pytra_sum(" + arg_strs[0] + ")"

    # range — handled by ForCore/RuntimeIterForPlan
    if bn == "range":
        return "__pytra_range(" + ", ".join(arg_strs) + ")"

    # Pathlib
    if rc == "py_write_text":
        func = node.get("func")
        if isinstance(func, dict):
            owner = _emit_expr(ctx, func.get("value"))
            if len(arg_strs) >= 1:
                return "__pytra_write_text(" + owner + ", " + arg_strs[0] + ")"

    # Generic: prefix with __pytra_
    fn_name = rc if rc != "" else bn
    if fn_name != "":
        return "__pytra_" + _safe_go_ident(fn_name) + "(" + ", ".join(arg_strs) + ")"

    return "nil /* unknown builtin */"


def _emit_attribute(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner = _emit_expr(ctx, node.get("value"))
    attr = _str(node, "attr")
    return owner + "." + _safe_go_ident(attr)


def _emit_subscript(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    value_node = node.get("value")
    value = _emit_expr(ctx, value_node)
    slice_node = node.get("slice")
    if isinstance(slice_node, dict) and _str(slice_node, "kind") == "Slice":
        return _emit_slice_access(ctx, value, slice_node)
    idx = _emit_expr(ctx, slice_node)
    # String indexing: wrap with __pytra_byte_to_string for str[int] → string
    if isinstance(value_node, dict):
        vt = _str(value_node, "resolved_type")
        if vt == "str":
            return "__pytra_byte_to_string(" + value + "[" + idx + "])"
    return value + "[" + idx + "]"


def _emit_slice_access(ctx: EmitContext, value: str, slice_node: dict[str, JsonVal]) -> str:
    lower = slice_node.get("lower")
    upper = slice_node.get("upper")
    lo = _emit_expr(ctx, lower) if lower is not None else ""
    hi = _emit_expr(ctx, upper) if upper is not None else ""
    return value + "[" + lo + ":" + hi + "]"


def _emit_slice_expr(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return "nil /* slice expr */"


def _emit_list_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elements = _list(node, "elements")
    rt = _str(node, "resolved_type")
    gt = go_type(rt)
    parts = [_emit_expr(ctx, e) for e in elements]
    return gt + "{" + ", ".join(parts) + "}"


def _emit_dict_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    keys = _list(node, "keys")
    values = _list(node, "values")
    rt = _str(node, "resolved_type")
    gt = go_type(rt)
    entries: list[str] = []
    for i in range(len(keys)):
        k = _emit_expr(ctx, keys[i]) if i < len(keys) else "nil"
        v = _emit_expr(ctx, values[i]) if i < len(values) else "nil"
        entries.append(k + ": " + v)
    return gt + "{" + ", ".join(entries) + "}"


def _emit_set_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elements = _list(node, "elements")
    parts = [_emit_expr(ctx, e) + ": {}" for e in elements]
    rt = _str(node, "resolved_type")
    gt = go_type(rt)
    return gt + "{" + ", ".join(parts) + "}"


def _emit_tuple_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elements = _list(node, "elements")
    parts = [_emit_expr(ctx, e) for e in elements]
    return "[]interface{}{" + ", ".join(parts) + "}"


def _emit_ifexp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    test = _emit_expr(ctx, node.get("test"))
    body = _emit_expr(ctx, node.get("body"))
    orelse = _emit_expr(ctx, node.get("orelse"))
    return "__pytra_ternary(" + test + ", " + body + ", " + orelse + ")"


def _emit_fstring(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    ctx.imports_needed.add("fmt")
    values = _list(node, "values")
    parts: list[str] = []
    for v in values:
        if isinstance(v, dict):
            if _str(v, "kind") == "Constant":
                val = v.get("value")
                if isinstance(val, str):
                    parts.append(_go_string_literal(val))
                    continue
            parts.append("fmt.Sprint(" + _emit_expr(ctx, v) + ")")
        else:
            parts.append("\"\"")
    if len(parts) == 0:
        return "\"\""
    if len(parts) == 1:
        return parts[0]
    return "(" + " + ".join(parts) + ")"


def _emit_formatted_value(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    ctx.imports_needed.add("fmt")
    value = _emit_expr(ctx, node.get("value"))
    fs = _str(node, "format_spec")
    if fs != "":
        return "fmt.Sprintf(\"%" + fs + "\", " + value + ")"
    return "fmt.Sprint(" + value + ")"


def _emit_lambda(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    arg_types = _dict(node, "arg_types")
    arg_order = _list(node, "arg_order")
    rt = _str(node, "return_type")
    body = node.get("body")

    params: list[str] = []
    for a in arg_order:
        a_name = a if isinstance(a, str) else ""
        a_type = arg_types.get(a_name, "")
        a_type_str = a_type if isinstance(a_type, str) else ""
        params.append(_safe_go_ident(a_name) + " " + go_type(a_type_str))

    return_type = go_type(rt)
    body_expr = _emit_expr(ctx, body)
    ret_clause = " " + return_type if return_type != "" else ""
    return "func(" + ", ".join(params) + ")" + ret_clause + " { return " + body_expr + " }"


def _emit_isinstance(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return "false /* isinstance not yet supported in Go */"


def _emit_list_comp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return "nil /* list comprehension */"


def _emit_set_comp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return "nil /* set comprehension */"


def _emit_dict_comp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return "nil /* dict comprehension */"


# ---------------------------------------------------------------------------
# Statement emission
# ---------------------------------------------------------------------------

def _emit_stmt(ctx: EmitContext, node: JsonVal) -> None:
    """Emit a statement node."""
    if not isinstance(node, dict):
        return

    kind = _str(node, "kind")

    if kind == "Expr":
        _emit_expr_stmt(ctx, node)
    elif kind == "AnnAssign":
        _emit_ann_assign(ctx, node)
    elif kind == "Assign":
        _emit_assign(ctx, node)
    elif kind == "AugAssign":
        _emit_aug_assign(ctx, node)
    elif kind == "Return":
        _emit_return(ctx, node)
    elif kind == "If":
        _emit_if(ctx, node)
    elif kind == "While":
        _emit_while(ctx, node)
    elif kind == "ForCore":
        _emit_for_core(ctx, node)
    elif kind == "RuntimeIterForPlan":
        _emit_runtime_iter_for(ctx, node)
    elif kind == "StaticRangeForPlan":
        _emit_static_range_for(ctx, node)
    elif kind == "FunctionDef":
        _emit_function_def(ctx, node)
    elif kind == "ClassDef":
        _emit_class_def(ctx, node)
    elif kind == "ImportFrom" or kind == "Import":
        pass  # Imports are handled at module level
    elif kind == "Pass":
        _emit(ctx, "// pass")
    elif kind == "VarDecl":
        _emit_var_decl(ctx, node)
    elif kind == "Swap":
        _emit_swap(ctx, node)
    elif kind == "Try":
        _emit_try(ctx, node)
    elif kind == "Raise":
        _emit_raise(ctx, node)
    elif kind == "TypeAlias":
        _emit_type_alias(ctx, node)
    elif kind == "comment":
        text = _str(node, "text")
        if text != "":
            _emit(ctx, "// " + text)
    elif kind == "blank":
        _emit_blank(ctx)
    else:
        _emit(ctx, "// unsupported stmt: " + kind)


def _emit_body(ctx: EmitContext, body: list[JsonVal]) -> None:
    for stmt in body:
        _emit_stmt(ctx, stmt)


def _emit_expr_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    value = node.get("value")
    if not isinstance(value, dict):
        return
    code = _emit_expr(ctx, value)
    if code != "":
        # Discard result if needed
        if _bool(value, "discard_result"):
            _emit(ctx, "_ = " + code)
        else:
            _emit(ctx, code)


def _emit_ann_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target_val = node.get("target")
    # Prefer decl_type over resolved_type for variable declarations
    rt = _str(node, "decl_type")
    if rt == "":
        rt = _str(node, "resolved_type")
    gt = go_type(rt)
    value = node.get("value")

    # target can be a string or a Name node dict
    target_name = ""
    if isinstance(target_val, str):
        target_name = target_val
    elif isinstance(target_val, dict):
        target_name = _str(target_val, "id")
        if target_name == "":
            target_name = _str(target_val, "repr")
    if target_name == "":
        tn = node.get("target_node")
        if isinstance(tn, dict):
            target_name = _str(tn, "id")
    name = _safe_go_ident(target_name)

    ctx.var_types[name] = rt

    if value is not None:
        val_code = _emit_expr(ctx, value)
        # Use typed declaration for numeric types to avoid Go's untyped int
        if gt in ("int64", "int32", "int16", "int8", "uint8", "uint16", "uint32", "uint64",
                  "float64", "float32"):
            _emit(ctx, "var " + name + " " + gt + " = " + val_code)
        else:
            _emit(ctx, name + " := " + val_code)
    else:
        _emit(ctx, "var " + name + " " + gt)


def _emit_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    targets = _list(node, "targets")
    value = node.get("value")

    # EAST3 may use "target" (single) or "targets" (list)
    target_single = node.get("target")
    if len(targets) == 0 and isinstance(target_single, dict):
        targets = [target_single]
    if len(targets) == 0:
        return

    val_code = _emit_expr(ctx, value)
    target_node = targets[0]
    if isinstance(target_node, dict):
        t_kind = _str(target_node, "kind")
        if t_kind == "Name" or t_kind == "NameTarget":
            name = _str(target_node, "id")
            if name == "":
                name = _str(target_node, "repr")
            gn = _safe_go_ident(name)
            if gn in ctx.var_types:
                _emit(ctx, gn + " = " + val_code)
            else:
                # Check for decl_type on the Assign node
                decl_type = _str(node, "decl_type")
                if decl_type == "":
                    decl_type = _str(target_node, "resolved_type")
                ctx.var_types[gn] = decl_type
                gt = go_type(decl_type)
                if gt in ("int64", "int32", "int16", "int8", "uint8", "uint16", "uint32", "uint64",
                          "float64", "float32"):
                    _emit(ctx, "var " + gn + " " + gt + " = " + val_code)
                else:
                    _emit(ctx, gn + " := " + val_code)
        elif t_kind == "Attribute":
            _emit(ctx, _emit_expr(ctx, target_node) + " = " + val_code)
        elif t_kind == "Subscript":
            _emit(ctx, _emit_expr(ctx, target_node) + " = " + val_code)
        elif t_kind == "Tuple":
            # Tuple unpack: a, b = expr
            elts = _list(target_node, "elements")
            names = [_emit_expr(ctx, e) for e in elts]
            _emit(ctx, ", ".join(names) + " = " + val_code)
        else:
            _emit(ctx, "_ = " + val_code + " // assign to " + t_kind)
    else:
        _emit(ctx, "_ = " + val_code)


def _emit_aug_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target = node.get("target")
    value = node.get("value")
    op = _str(node, "op")
    go_op = _BINOP_MAP.get(op, "+")
    t_code = _emit_expr(ctx, target)
    v_code = _emit_expr(ctx, value)
    _emit(ctx, t_code + " " + go_op + "= " + v_code)


def _emit_return(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    value = node.get("value")
    if value is None:
        _emit(ctx, "return")
    else:
        _emit(ctx, "return " + _emit_expr(ctx, value))


def _emit_if(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    test = _emit_expr(ctx, node.get("test"))
    _emit(ctx, "if " + test + " {")
    ctx.indent_level += 1
    _emit_body(ctx, _list(node, "body"))
    ctx.indent_level -= 1
    orelse = _list(node, "orelse")
    if len(orelse) > 0:
        if len(orelse) == 1 and isinstance(orelse[0], dict) and _str(orelse[0], "kind") == "If":
            _emit(ctx, "} else ")
            # Inline the else-if without extra brace
            ctx.lines[-1] = ctx.lines[-1].rstrip()  # remove trailing newline
            _emit_if(ctx, orelse[0])
            return
        _emit(ctx, "} else {")
        ctx.indent_level += 1
        _emit_body(ctx, orelse)
        ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_while(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    test = _emit_expr(ctx, node.get("test"))
    _emit(ctx, "for " + test + " {")
    ctx.indent_level += 1
    _emit_body(ctx, _list(node, "body"))
    ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_for_core(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    body = _list(node, "body")

    # ForCore uses iter_plan + target_plan (EAST3 lowered form)
    iter_plan = node.get("iter_plan")
    target_plan = node.get("target_plan")

    if isinstance(iter_plan, dict):
        ip_kind = _str(iter_plan, "kind")
        t_name = ""
        if isinstance(target_plan, dict):
            t_name = _str(target_plan, "id")
        t_name = _safe_go_ident(t_name) if t_name != "" else "_"

        if ip_kind == "StaticRangeForPlan":
            _emit_range_for(ctx, t_name, iter_plan, body)
            return
        if ip_kind == "RuntimeIterForPlan":
            # Check if this is a range (has start/stop) or a collection iter (has iter_expr)
            if iter_plan.get("start") is not None or iter_plan.get("stop") is not None:
                _emit_range_for(ctx, t_name, iter_plan, body)
            else:
                # Collection iterator: for _, item := range collection
                iter_expr = iter_plan.get("iter_expr")
                iter_code = _emit_expr(ctx, iter_expr) if iter_expr is not None else "nil"
                _emit(ctx, "for _, " + t_name + " := range " + iter_code + " {")
                ctx.indent_level += 1
                ctx.var_types[t_name] = ""
                _emit_body(ctx, body)
                ctx.indent_level -= 1
                _emit(ctx, "}")
            return

    # Fallback: legacy target/iter form
    target = node.get("target")
    iter_expr = node.get("iter")

    t_name = ""
    if isinstance(target, dict):
        t_name = _str(target, "id")
        if t_name == "":
            t_name = _str(target, "repr")
    t_name = _safe_go_ident(t_name) if t_name != "" else "_"

    iter_code = _emit_expr(ctx, iter_expr)
    _emit(ctx, "for _, " + t_name + " := range " + iter_code + " {")
    ctx.indent_level += 1
    ctx.var_types[t_name] = ""
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_range_for(ctx: EmitContext, t_name: str, plan: dict[str, JsonVal], body: list[JsonVal]) -> None:
    """Emit a range-based for loop from StaticRangeForPlan or RuntimeIterForPlan."""
    start = plan.get("start")
    stop = plan.get("stop")
    step = plan.get("step")

    s_code = _emit_expr(ctx, start) if start is not None else "0"
    e_code = _emit_expr(ctx, stop) if stop is not None else "0"

    # Determine step
    step_code = "1"
    step_negative = False
    if isinstance(step, dict) and _str(step, "kind") == "Constant":
        sv = step.get("value")
        if isinstance(sv, int):
            step_code = str(sv)
            step_negative = sv < 0
    elif step is not None:
        step_code = _emit_expr(ctx, step)

    cmp_op = " > " if step_negative else " < "
    _emit(ctx, "for " + t_name + " := int64(" + s_code + "); " + t_name + cmp_op + e_code + "; " + t_name + " += " + step_code + " {")
    ctx.indent_level += 1
    ctx.var_types[t_name] = "int64"
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_runtime_iter_for(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    """RuntimeIterForPlan as standalone statement (outside ForCore)."""
    target = node.get("target")
    body = _list(node, "body")
    t_name = ""
    if isinstance(target, dict):
        t_name = _str(target, "id")
    t_name = _safe_go_ident(t_name) if t_name != "" else "_"
    _emit_range_for(ctx, t_name, node, body)


def _emit_static_range_for(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    """StaticRangeForPlan as standalone statement (outside ForCore)."""
    _emit_runtime_iter_for(ctx, node)


def _emit_function_def(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    arg_types = _dict(node, "arg_types")
    arg_order = _list(node, "arg_order")
    return_type = _str(node, "return_type")
    body = _list(node, "body")
    decorators = _list(node, "decorators")

    # Skip extern declarations
    for d in decorators:
        if isinstance(d, str) and d == "extern":
            return

    fn_name = _safe_go_ident(name)
    go_ret = go_type(return_type)

    # Build params
    params: list[str] = []
    saved_vars = dict(ctx.var_types)
    for a in arg_order:
        a_str = a if isinstance(a, str) else ""
        if a_str == "self":
            continue
        a_type_val = arg_types.get(a_str, "")
        a_type = a_type_val if isinstance(a_type_val, str) else ""
        ga = _safe_go_ident(a_str)
        gt = go_type(a_type)
        params.append(ga + " " + gt)
        ctx.var_types[ga] = a_type

    # Method vs function
    if ctx.current_class != "":
        receiver = ctx.current_receiver + " *" + _safe_go_ident(ctx.current_class)
        ret_clause = " " + go_ret if go_ret != "" and return_type != "None" else ""
        _emit(ctx, "func (" + receiver + ") " + fn_name + "(" + ", ".join(params) + ")" + ret_clause + " {")
    else:
        ret_clause = " " + go_ret if go_ret != "" and return_type != "None" else ""
        _emit(ctx, "func " + fn_name + "(" + ", ".join(params) + ")" + ret_clause + " {")

    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")
    _emit_blank(ctx)

    ctx.var_types = saved_vars


def _emit_class_def(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    base = _str(node, "base")
    body = _list(node, "body")
    gn = _safe_go_ident(name)
    is_dataclass = _bool(node, "dataclass")

    ctx.class_names.add(name)
    if base != "":
        ctx.class_bases[name] = base

    # Collect fields: prefer field_types (dataclass), else scan __init__
    fields: list[tuple[str, str]] = []
    field_types = _dict(node, "field_types")
    if len(field_types) > 0:
        for fname_key, ftype_val in field_types.items():
            ft = ftype_val if isinstance(ftype_val, str) else ""
            fields.append((fname_key, ft))
    else:
        # Scan body AnnAssign (dataclass fields) or __init__
        for stmt in body:
            if not isinstance(stmt, dict):
                continue
            sk = _str(stmt, "kind")
            if sk == "AnnAssign" and is_dataclass:
                target_val = stmt.get("target")
                ft_name = ""
                if isinstance(target_val, dict):
                    ft_name = _str(target_val, "id")
                elif isinstance(target_val, str):
                    ft_name = target_val
                frt = _str(stmt, "decl_type")
                if frt == "":
                    frt = _str(stmt, "resolved_type")
                if ft_name != "":
                    fields.append((ft_name, frt))
            elif sk == "FunctionDef" and _str(stmt, "name") == "__init__":
                for init_stmt in _list(stmt, "body"):
                    if isinstance(init_stmt, dict) and _str(init_stmt, "kind") == "AnnAssign":
                        t_val = init_stmt.get("target")
                        ft = ""
                        if isinstance(t_val, dict):
                            ft = _str(t_val, "id")
                        elif isinstance(t_val, str):
                            ft = t_val
                        frt = _str(init_stmt, "decl_type")
                        if frt == "":
                            frt = _str(init_stmt, "resolved_type")
                        if ft.startswith("self."):
                            ft = ft[5:]
                        if ft != "":
                            fields.append((ft, frt))

    # Struct definition
    _emit(ctx, "type " + gn + " struct {")
    ctx.indent_level += 1
    if base != "" and base not in ("object", "Exception", "BaseException"):
        _emit(ctx, _safe_go_ident(base))  # embed base
    for fname, ftype in fields:
        _emit(ctx, _safe_go_ident(fname) + " " + go_type(ftype))
    ctx.indent_level -= 1
    _emit(ctx, "}")
    _emit_blank(ctx)

    # Constructor
    _emit(ctx, "func New" + gn + "(" + ", ".join(
        _safe_go_ident(f) + " " + go_type(t) for f, t in fields
    ) + ") *" + gn + " {")
    ctx.indent_level += 1
    field_inits = ", ".join(_safe_go_ident(f) + ": " + _safe_go_ident(f) for f, _ in fields)
    _emit(ctx, "return &" + gn + "{" + field_inits + "}")
    ctx.indent_level -= 1
    _emit(ctx, "}")
    _emit_blank(ctx)

    # Methods
    saved_class = ctx.current_class
    saved_receiver = ctx.current_receiver
    ctx.current_class = name
    ctx.current_receiver = "self"
    for stmt in body:
        if isinstance(stmt, dict) and _str(stmt, "kind") == "FunctionDef":
            fn_name = _str(stmt, "name")
            if fn_name == "__init__":
                continue  # Already handled by constructor
            _emit_function_def(ctx, stmt)
    ctx.current_class = saved_class
    ctx.current_receiver = saved_receiver


def _emit_var_decl(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    rt = _str(node, "resolved_type")
    gt = go_type(rt)
    gn = _safe_go_ident(name)
    ctx.var_types[gn] = rt
    _emit(ctx, "var " + gn + " " + gt)


def _emit_swap(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    left = _emit_expr(ctx, node.get("left"))
    right = _emit_expr(ctx, node.get("right"))
    _emit(ctx, left + ", " + right + " = " + right + ", " + left)


def _emit_try(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    _emit(ctx, "func() {")
    ctx.indent_level += 1
    _emit(ctx, "defer func() {")
    ctx.indent_level += 1
    _emit(ctx, "if r := recover(); r != nil {")
    ctx.indent_level += 1
    handlers = _list(node, "handlers")
    if len(handlers) > 0:
        handler = handlers[0]
        if isinstance(handler, dict):
            _emit_body(ctx, _list(handler, "body"))
    ctx.indent_level -= 1
    _emit(ctx, "}")
    ctx.indent_level -= 1
    _emit(ctx, "}()")
    _emit_body(ctx, _list(node, "body"))
    ctx.indent_level -= 1
    _emit(ctx, "}()")
    finalbody = _list(node, "finalbody")
    if len(finalbody) > 0:
        _emit_body(ctx, finalbody)


def _emit_raise(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    exc = node.get("exc")
    if exc is not None:
        _emit(ctx, "panic(" + _emit_expr(ctx, exc) + ")")
    else:
        _emit(ctx, "panic(nil)")


def _emit_type_alias(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    _emit(ctx, "// type alias: " + name)


# ---------------------------------------------------------------------------
# Module emission (top-level)
# ---------------------------------------------------------------------------

def emit_go_module(east3_doc: dict[str, JsonVal]) -> str:
    """Emit a complete Go source file from an EAST3 document.

    Args:
        east3_doc: linked EAST3 JSON dict with meta.linked_program_v1.

    Returns:
        Go source code string, or empty string if the module should be skipped.
    """
    meta = _dict(east3_doc, "meta")
    module_id = ""

    # Get module_id from emit_context or linked_program_v1
    emit_ctx_meta = _dict(meta, "emit_context")
    if emit_ctx_meta:
        module_id = _str(emit_ctx_meta, "module_id")

    lp = _dict(meta, "linked_program_v1")
    if module_id == "" and lp:
        module_id = _str(lp, "module_id")

    # Skip built-in modules (provided by py_runtime.go)
    if module_id.startswith("pytra.built_in."):
        return ""

    ctx = EmitContext(
        module_id=module_id,
        is_entry=_bool(emit_ctx_meta, "is_entry") if emit_ctx_meta else False,
    )

    body = _list(east3_doc, "body")
    main_guard = _list(east3_doc, "main_guard_body")

    # First pass: collect class names
    for stmt in body:
        if isinstance(stmt, dict) and _str(stmt, "kind") == "ClassDef":
            ctx.class_names.add(_str(stmt, "name"))

    # Emit body
    for stmt in body:
        _emit_stmt(ctx, stmt)

    # Emit main guard
    if len(main_guard) > 0:
        _emit_blank(ctx)
        _emit(ctx, "func _main_guard() {")
        ctx.indent_level += 1
        for stmt in main_guard:
            _emit_stmt(ctx, stmt)
        ctx.indent_level -= 1
        _emit(ctx, "}")

    # Generate main() for entry module
    if ctx.is_entry or len(main_guard) > 0:
        _emit_blank(ctx)
        _emit(ctx, "func main() {")
        ctx.indent_level += 1
        _emit(ctx, "_main_guard()")
        ctx.indent_level -= 1
        _emit(ctx, "}")

    # Build final source
    header_lines: list[str] = ["package main", ""]

    # Imports
    if len(ctx.imports_needed) > 0:
        header_lines.append("import (")
        for imp in sorted(ctx.imports_needed):
            header_lines.append('\t"' + imp + '"')
        header_lines.append(")")
        header_lines.append("")

    return "\n".join(header_lines + ctx.lines) + "\n"
