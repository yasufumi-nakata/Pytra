"""EAST3 -> PowerShell native emitter.

This backend emits native PowerShell code directly from EAST3 IR,
without going through an intermediate JavaScript representation.
"""

from __future__ import annotations

from typing import Any

from backends.common.emitter.code_emitter import (
    reject_backend_general_union_type_exprs,
    reject_backend_typed_vararg_signatures,
)


_PS_KEYWORDS = {
    "begin", "break", "catch", "class", "continue", "data", "do", "dynamicparam",
    "else", "elseif", "end", "enum", "exit", "filter", "finally", "for",
    "foreach", "from", "function", "if", "in", "param", "process", "return",
    "switch", "throw", "trap", "try", "until", "using", "while",
}

_PS_AUTOMATIC_VARS = {
    "true", "false", "null", "args", "input", "PSScriptRoot", "PSCommandPath",
    "Error", "Host", "HOME", "PID", "PROFILE",
}


def _safe_ident(name: Any, fallback: str) -> str:
    if not isinstance(name, str) or name == "":
        return fallback
    chars: list[str] = []
    for ch in name:
        if ch.isalnum() or ch == "_":
            chars.append(ch)
        else:
            chars.append("_")
    out = "".join(chars)
    if out == "":
        out = fallback
    if out[0].isdigit():
        out = "_" + out
    if out in _PS_KEYWORDS:
        out = out + "_"
    return out


def _ps_string_literal(text: str) -> str:
    out = text.replace("`", "``")
    out = out.replace('"', '`"')
    out = out.replace("$", "`$")
    out = out.replace("\n", "`n")
    out = out.replace("\r", "`r")
    out = out.replace("\t", "`t")
    out = out.replace("\0", "`0")
    return '"' + out + '"'


def _get_str(d: dict[str, Any], key: str) -> str:
    v = d.get(key)
    return v if isinstance(v, str) else ""


def _get_list(d: dict[str, Any], key: str) -> list[Any]:
    v = d.get(key)
    return v if isinstance(v, list) else []


def _get_dict(d: dict[str, Any], key: str) -> dict[str, Any]:
    v = d.get(key)
    return v if isinstance(v, dict) else {}


# ---------------------------------------------------------------------------
# Expression rendering
# ---------------------------------------------------------------------------

_BINOP_MAP: dict[str, str] = {
    "Add": "+",
    "Sub": "-",
    "Mult": "*",
    "Div": "/",
    "Mod": "%",
    "BitAnd": "-band",
    "BitOr": "-bor",
    "BitXor": "-bxor",
    "LShift": "-shl",
    "RShift": "-shr",
    "FloorDiv": "/",
    "Pow": "",
}

_COMPARE_MAP: dict[str, str] = {
    "Eq": "-eq",
    "NotEq": "-ne",
    "Lt": "-lt",
    "LtE": "-le",
    "Gt": "-gt",
    "GtE": "-ge",
    "Is": "-eq",
    "IsNot": "-ne",
}

_UNARYOP_MAP: dict[str, str] = {
    "USub": "-",
    "UAdd": "+",
    "Not": "-not ",
    "Invert": "-bnot ",
}


def _render_expr(expr_any: Any) -> str:
    if not isinstance(expr_any, dict):
        if isinstance(expr_any, bool):
            return "$true" if expr_any else "$false"
        if isinstance(expr_any, int):
            return str(expr_any)
        if isinstance(expr_any, float):
            return str(expr_any)
        if isinstance(expr_any, str):
            return _ps_string_literal(expr_any)
        return "$null"

    expr: dict[str, object] = expr_any
    kind = _get_str(expr, "kind")

    if kind == "Name":
        raw = _get_str(expr, "id")
        if raw == "True" or raw == "true":
            return "$true"
        if raw == "False" or raw == "false":
            return "$false"
        if raw == "None" or raw == "null" or raw == "undefined":
            return "$null"
        return "$" + _safe_ident(raw, "_v")

    if kind == "Constant":
        value = expr.get("value")
        if value is None:
            return "$null"
        if isinstance(value, bool):
            return "$true" if value else "$false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            s = repr(value)
            if "inf" in s.lower():
                return "[double]::PositiveInfinity" if value > 0 else "[double]::NegativeInfinity"
            return s
        if isinstance(value, str):
            return _ps_string_literal(value)
        return "$null"

    if kind == "UnaryOp":
        op = _get_str(expr, "op")
        operand = _render_expr(expr.get("operand"))
        ps_op = _UNARYOP_MAP.get(op, "-")
        return "(" + ps_op + operand + ")"

    if kind == "BinOp":
        op = _get_str(expr, "op")
        left = _render_expr(expr.get("left"))
        right = _render_expr(expr.get("right"))
        if op == "Pow":
            return "[Math]::Pow(" + left + ", " + right + ")"
        if op == "FloorDiv":
            return "[Math]::Floor(" + left + " / " + right + ")"
        ps_op = _BINOP_MAP.get(op, "+")
        return "(" + left + " " + ps_op + " " + right + ")"

    if kind == "Compare":
        left = _render_expr(expr.get("left"))
        ops = _get_list(expr, "ops")
        comparators = _get_list(expr, "comparators")
        if len(ops) == 0 or len(comparators) == 0:
            return "$true"
        op0 = ops[0]
        if isinstance(op0, dict):
            op0_d: dict[str, object] = op0
            ps_op = _COMPARE_MAP.get(_get_str(op0_d, "kind"), "-eq")
        elif isinstance(op0, str):
            ps_op = _COMPARE_MAP.get(op0, "-eq")
        else:
            ps_op = "-eq"
        right = _render_expr(comparators[0])
        if len(ops) == 1:
            return "(" + left + " " + ps_op + " " + right + ")"
        parts = ["(" + left + " " + ps_op + " " + right + ")"]
        i = 1
        while i < len(ops) and i < len(comparators):
            prev_right = _render_expr(comparators[i - 1])
            op_str = ops[i] if isinstance(ops[i], str) else ""
            next_op = _COMPARE_MAP.get(op_str, "-eq")
            next_right = _render_expr(comparators[i])
            parts.append("(" + prev_right + " " + next_op + " " + next_right + ")")
            i += 1
        return "(" + " -and ".join(parts) + ")"

    if kind == "BoolOp":
        op = _get_str(expr, "op")
        values = _get_list(expr, "values")
        ps_op = "-and" if op == "And" else "-or"
        rendered = [_render_expr(v) for v in values]
        return "(" + (" " + ps_op + " ").join(rendered) + ")"

    if kind == "Attribute":
        value = _render_expr(expr.get("value"))
        attr = _safe_ident(_get_str(expr, "attr"), "prop")
        return value + "." + attr

    if kind == "Call":
        return _render_call_expr(expr)

    if kind == "List" or kind == "Tuple":
        elements = _get_list(expr, "elements")
        if len(elements) == 0:
            elements = _get_list(expr, "elts")
        if len(elements) == 0:
            return "@()"
        rendered = [_render_expr(e) for e in elements]
        return "@(" + ", ".join(rendered) + ")"

    if kind == "Dict":
        keys = _get_list(expr, "keys")
        vals = _get_list(expr, "values")
        if len(keys) == 0 and len(vals) == 0:
            entries = _get_list(expr, "entries")
            for entry in entries:
                if isinstance(entry, dict):
                    entry_d: dict[str, object] = entry
                    k = entry_d.get("key")
                    v = entry_d.get("value")
                    if k is not None:
                        keys.append(k)
                    if v is not None:
                        vals.append(v)
        if len(keys) == 0:
            return "@{}"
        parts: list[str] = []
        i = 0
        while i < len(keys) and i < len(vals):
            parts.append(_render_expr(keys[i]) + " = " + _render_expr(vals[i]))
            i += 1
        return "@{" + "; ".join(parts) + "}"

    if kind == "Subscript":
        value = _render_expr(expr.get("value"))
        slice_any = expr.get("slice")
        if isinstance(slice_any, dict) and _get_str(slice_any, "kind") == "Slice":
            slice_d: dict[str, object] = slice_any
            lower = _render_expr(slice_d.get("lower")) if slice_d.get("lower") is not None else "0"
            upper = _render_expr(slice_d.get("upper")) if slice_d.get("upper") is not None else (value + ".Length")
            return value + "[" + lower + "..(" + upper + " - 1)]"
        index = _render_expr(slice_any)
        return value + "[" + index + "]"

    if kind == "IfExp":
        test = _render_expr(expr.get("test"))
        body = _render_expr(expr.get("body"))
        orelse = _render_expr(expr.get("orelse"))
        return "$(if (" + test + ") { " + body + " } else { " + orelse + " })"

    if kind == "JoinedStr" or kind == "FString":
        parts_list = _get_list(expr, "values")
        if len(parts_list) == 0:
            return '""'
        segments: list[str] = []
        for part in parts_list:
            if not isinstance(part, dict):
                continue
            part_d: dict[str, object] = part
            pk = _get_str(part_d, "kind")
            if pk == "Constant":
                v = part_d.get("value")
                if isinstance(v, str):
                    escaped = v.replace("`", "``").replace('"', '`"').replace("$", "`$")
                    segments.append(escaped)
            elif pk == "FormattedValue":
                inner = _render_expr(part_d.get("value"))
                segments.append("$(" + inner + ")")
            else:
                segments.append("$(" + _render_expr(part_d) + ")")
        return '"' + "".join(segments) + '"'

    if kind == "IsInstance":
        return "$true"

    if kind == "ObjLen":
        return "__pytra_len " + _render_expr(expr.get("value"))

    if kind == "ObjStr":
        return "__pytra_str " + _render_expr(expr.get("value"))

    if kind == "ObjBool":
        return "__pytra_bool " + _render_expr(expr.get("value"))

    if kind == "Box":
        return _render_expr(expr.get("value"))

    if kind == "Unbox":
        return _render_expr(expr.get("value"))

    if kind == "RangeExpr":
        start = _render_expr(expr.get("start"))
        stop = _render_expr(expr.get("stop"))
        step = expr.get("step")
        if step is not None:
            return "__pytra_range " + start + " " + stop + " " + _render_expr(step)
        return "__pytra_range " + start + " " + stop

    if kind == "Lambda":
        params = _get_list(expr, "params")
        body = expr.get("body")
        lambda_param_names: list[str] = []
        for p in params:
            if isinstance(p, dict):
                lp_d: dict[str, object] = p
                lambda_param_names.append("$" + _safe_ident(_get_str(lp_d, "arg"), "_p"))
            else:
                lambda_param_names.append("$" + _safe_ident(str(p), "_p"))
        ps_params = ", ".join(lambda_param_names)
        return "{ param(" + ps_params + ") " + _render_expr(body) + " }"

    return "$null"


def _render_call_expr(expr: dict[str, Any]) -> str:
    func = expr.get("func")
    args = _get_list(expr, "args")
    rendered_args = [_render_expr(a) for a in args]

    if isinstance(func, dict):
        func_d: dict[str, object] = func
        fk = _get_str(func_d, "kind")

        if fk == "Name":
            fn_name = _get_str(func_d, "id")
            if fn_name == "print":
                return "__pytra_print " + " ".join(rendered_args) if len(rendered_args) > 0 else "__pytra_print"
            if fn_name == "len":
                return "__pytra_len " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_len"
            if fn_name == "str":
                return "__pytra_str " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_str"
            if fn_name == "int":
                return "__pytra_int " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_int"
            if fn_name == "float":
                return "__pytra_float " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_float"
            if fn_name == "bool":
                return "__pytra_bool " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_bool"
            if fn_name == "range":
                return "__pytra_range " + " ".join(rendered_args)
            if fn_name == "ord":
                return "__pytra_ord " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_ord"
            if fn_name == "chr":
                return "__pytra_chr " + rendered_args[0] if len(rendered_args) > 0 else "__pytra_chr"
            if fn_name == "abs":
                return "[Math]::Abs(" + rendered_args[0] + ")" if len(rendered_args) > 0 else "[Math]::Abs(0)"
            if fn_name == "min":
                return "[Math]::Min(" + ", ".join(rendered_args) + ")" if len(rendered_args) > 0 else "0"
            if fn_name == "max":
                return "[Math]::Max(" + ", ".join(rendered_args) + ")" if len(rendered_args) > 0 else "0"
            if fn_name == "isinstance":
                return "$true"
            safe = _safe_ident(fn_name, "_fn")
            if len(rendered_args) == 0:
                return safe
            return safe + " " + " ".join(rendered_args)

        if fk == "Attribute":
            owner = _render_expr(func_d.get("value"))
            attr = _safe_ident(_get_str(func_d, "attr"), "method")
            if attr == "append":
                if len(rendered_args) > 0:
                    return owner + " += @(" + rendered_args[0] + ")"
                return owner
            if attr == "join":
                if len(rendered_args) > 0:
                    return "(" + rendered_args[0] + " -join " + owner + ")"
                return owner
            if attr == "format":
                return owner + " -f " + ", ".join(rendered_args) if len(rendered_args) > 0 else owner
            if attr == "startswith":
                return owner + ".StartsWith(" + ", ".join(rendered_args) + ")"
            if attr == "endswith":
                return owner + ".EndsWith(" + ", ".join(rendered_args) + ")"
            if attr == "upper":
                return owner + ".ToUpper()"
            if attr == "lower":
                return owner + ".ToLower()"
            if attr == "strip":
                return owner + ".Trim()"
            if attr == "split":
                if len(rendered_args) > 0:
                    return owner + ".Split(" + rendered_args[0] + ")"
                return owner + ".Split()"
            if attr == "replace":
                if len(rendered_args) >= 2:
                    return owner + ".Replace(" + rendered_args[0] + ", " + rendered_args[1] + ")"
                return owner
            if attr == "keys":
                return owner + ".Keys"
            if attr == "values":
                return owner + ".Values"
            if attr == "items":
                return owner + ".GetEnumerator()"
            if attr == "get":
                if len(rendered_args) >= 2:
                    return "$(if (" + owner + ".ContainsKey(" + rendered_args[0] + ")) { " + owner + "[" + rendered_args[0] + "] } else { " + rendered_args[1] + " })"
                if len(rendered_args) == 1:
                    return owner + "[" + rendered_args[0] + "]"
                return "$null"
            if attr == "pop":
                if len(rendered_args) == 0:
                    return owner + "[-1]; " + owner + " = " + owner + "[0..(" + owner + ".Length - 2)]"
                return owner
            if len(rendered_args) == 0:
                return owner + "." + attr + "()"
            return owner + "." + attr + "(" + ", ".join(rendered_args) + ")"

    fn_rendered = _render_expr(func)
    if len(rendered_args) == 0:
        return fn_rendered
    return fn_rendered + " " + " ".join(rendered_args)


# ---------------------------------------------------------------------------
# Statement emission
# ---------------------------------------------------------------------------

def _emit_body(body: list[Any], *, indent: str, ctx: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for stmt in body:
        if isinstance(stmt, dict):
            stmt_d: dict[str, object] = stmt
            lines.extend(_emit_stmt(stmt_d, indent=indent, ctx=ctx))
    if len(lines) == 0:
        lines.append(indent + "# pass")
    return lines


def _emit_stmt(stmt: dict[str, Any], *, indent: str, ctx: dict[str, Any]) -> list[str]:
    kind = _get_str(stmt, "kind")

    if kind == "Expr":
        value = stmt.get("value")
        if isinstance(value, dict):
            value_d: dict[str, object] = value
            vk = _get_str(value_d, "kind")
            if vk == "Name":
                raw = _get_str(value_d, "id")
                if raw == "break":
                    return [indent + "break"]
                if raw == "continue":
                    return [indent + "continue"]
                if raw == "pass":
                    return [indent + "# pass"]
        return [indent + _render_expr(value)]

    if kind == "Return":
        value = stmt.get("value")
        if value is not None:
            return [indent + "return " + _render_expr(value)]
        return [indent + "return"]

    if kind == "Assign":
        targets = _get_list(stmt, "targets")
        if len(targets) == 0:
            t = stmt.get("target")
            if isinstance(t, dict):
                targets = [t]
        value = _render_expr(stmt.get("value"))
        if len(targets) == 0:
            return [indent + value]
        target = targets[0]
        if isinstance(target, dict):
            target_d: dict[str, object] = target
            if _get_str(target_d, "kind") == "Attribute":
                return [indent + _render_expr(target_d) + " = " + value]
            if _get_str(target_d, "kind") == "Subscript":
                owner = _render_expr(target_d.get("value"))
                index = _render_expr(target_d.get("slice"))
                return [indent + owner + "[" + index + "] = " + value]
        lhs = _render_expr(target)
        return [indent + lhs + " = " + value]

    if kind == "AnnAssign":
        target = stmt.get("target")
        value = stmt.get("value")
        if value is None:
            lhs = _render_expr(target)
            return [indent + lhs + " = $null"]
        lhs = _render_expr(target)
        return [indent + lhs + " = " + _render_expr(value)]

    if kind == "AugAssign":
        target = _render_expr(stmt.get("target"))
        op = _get_str(stmt, "op")
        value = _render_expr(stmt.get("value"))
        op_map: dict[str, str] = {
            "Add": "+=", "Sub": "-=", "Mult": "*=", "Div": "/=",
            "Mod": "%=", "BitAnd": "=", "BitOr": "=", "BitXor": "=",
            "LShift": "=", "RShift": "=",
        }
        ps_op = op_map.get(op, "=")
        if ps_op == "=" and op in _BINOP_MAP:
            return [indent + target + " = (" + target + " " + _BINOP_MAP[op] + " " + value + ")"]
        return [indent + target + " " + ps_op + " " + value]

    if kind == "If":
        test = _render_expr(stmt.get("test"))
        body = _get_list(stmt, "body")
        orelse = _get_list(stmt, "orelse")
        lines = [indent + "if (" + test + ") {"]
        lines.extend(_emit_body(body, indent=indent + "    ", ctx=ctx))
        if len(orelse) > 0:
            if len(orelse) == 1 and isinstance(orelse[0], dict) and _get_str(orelse[0], "kind") == "If":
                inner_d: dict[str, object] = orelse[0]
                lines.append(indent + "} elseif (" + _render_expr(inner_d.get("test")) + ") {")
                lines.extend(_emit_body(_get_list(inner_d, "body"), indent=indent + "    ", ctx=ctx))
                inner_else = _get_list(inner_d, "orelse")
                while len(inner_else) == 1 and isinstance(inner_else[0], dict) and _get_str(inner_else[0], "kind") == "If":
                    next_if: dict[str, object] = inner_else[0]
                    inner_d = next_if
                    lines.append(indent + "} elseif (" + _render_expr(inner_d.get("test")) + ") {")
                    lines.extend(_emit_body(_get_list(inner_d, "body"), indent=indent + "    ", ctx=ctx))
                    inner_else = _get_list(inner_d, "orelse")
                if len(inner_else) > 0:
                    lines.append(indent + "} else {")
                    lines.extend(_emit_body(inner_else, indent=indent + "    ", ctx=ctx))
            else:
                lines.append(indent + "} else {")
                lines.extend(_emit_body(orelse, indent=indent + "    ", ctx=ctx))
        lines.append(indent + "}")
        return lines

    if kind == "While":
        test = _render_expr(stmt.get("test"))
        body = _get_list(stmt, "body")
        lines = [indent + "while (" + test + ") {"]
        lines.extend(_emit_body(body, indent=indent + "    ", ctx=ctx))
        lines.append(indent + "}")
        return lines

    if kind == "ForCore":
        init = stmt.get("init")
        test = stmt.get("test")
        update = stmt.get("update")
        body = _get_list(stmt, "body")
        if isinstance(init, dict):
            init_d: dict[str, object] = init
            init_str = _render_expr(init_d.get("value")) if init_d.get("value") is not None else "$null"
            init_target = _render_expr(init_d.get("target"))
        else:
            init_str = "$null"
            init_target = "$_i"
        test_str = _render_expr(test) if test is not None else "$true"
        update_str = ""
        if isinstance(update, dict):
            update_d: dict[str, object] = update
            uk = _get_str(update_d, "kind")
            if uk == "AugAssign":
                update_str = _render_expr(update_d.get("target")) + " += " + _render_expr(update_d.get("value"))
            else:
                update_str = _render_expr(update_d)
        lines = [indent + "for (" + init_target + " = " + init_str + "; " + test_str + "; " + update_str + ") {"]
        lines.extend(_emit_body(body, indent=indent + "    ", ctx=ctx))
        lines.append(indent + "}")
        return lines

    if kind == "For":
        target = stmt.get("target")
        iter_expr = stmt.get("iter")
        body = _get_list(stmt, "body")
        target_str = _render_expr(target) if target is not None else "$_item"
        iter_str = _render_expr(iter_expr) if iter_expr is not None else "@()"
        lines = [indent + "foreach (" + target_str + " in " + iter_str + ") {"]
        lines.extend(_emit_body(body, indent=indent + "    ", ctx=ctx))
        lines.append(indent + "}")
        return lines

    if kind == "Try":
        body = _get_list(stmt, "body")
        handlers = _get_list(stmt, "handlers")
        finalbody = _get_list(stmt, "finalbody")
        lines = [indent + "try {"]
        lines.extend(_emit_body(body, indent=indent + "    ", ctx=ctx))
        for handler in handlers:
            if not isinstance(handler, dict):
                continue
            handler_d: dict[str, object] = handler
            handler_name = _get_str(handler_d, "name")
            if handler_name != "":
                lines.append(indent + "} catch {")
                lines.append(indent + "    $" + _safe_ident(handler_name, "e") + " = $_")
            else:
                lines.append(indent + "} catch {")
            handler_body = _get_list(handler_d, "body")
            lines.extend(_emit_body(handler_body, indent=indent + "    ", ctx=ctx))
        if len(handlers) == 0:
            lines.append(indent + "} catch {")
            lines.append(indent + "    # unhandled")
        if len(finalbody) > 0:
            lines.append(indent + "} finally {")
            lines.extend(_emit_body(finalbody, indent=indent + "    ", ctx=ctx))
        lines.append(indent + "}")
        return lines

    if kind == "Raise":
        exc = stmt.get("exc")
        if exc is not None:
            return [indent + "throw " + _render_expr(exc)]
        return [indent + "throw"]

    if kind == "Pass":
        return [indent + "# pass"]

    if kind == "Break":
        return [indent + "break"]

    if kind == "Continue":
        return [indent + "continue"]

    if kind == "Swap":
        left = _render_expr(stmt.get("left"))
        right = _render_expr(stmt.get("right"))
        tmp = "$__swap_tmp"
        return [
            indent + tmp + " = " + left,
            indent + left + " = " + right,
            indent + right + " = " + tmp,
        ]

    if kind == "FunctionDef":
        return _emit_function_def(stmt, indent=indent, ctx=ctx)

    if kind == "ClassDef":
        return _emit_class_def(stmt, indent=indent, ctx=ctx)

    if kind == "ImportFrom":
        return [indent + "# import: " + _get_str(stmt, "module")]

    if kind == "Import":
        return [indent + "# import"]

    return [indent + "# unsupported: " + kind]


def _emit_function_def(stmt: dict[str, Any], *, indent: str, ctx: dict[str, Any]) -> list[str]:
    name = _safe_ident(_get_str(stmt, "name"), "_fn")
    params = _get_list(stmt, "params")
    if len(params) == 0:
        params = _get_list(stmt, "args")
    body = _get_list(stmt, "body")

    ps_params: list[str] = []
    for p in params:
        if isinstance(p, dict):
            p_d: dict[str, object] = p
            arg_name = _get_str(p_d, "arg")
            if arg_name == "" :
                arg_name = _get_str(p_d, "name")
            if arg_name == "self":
                continue
            default = p_d.get("default")
            if default is not None:
                ps_params.append("$" + _safe_ident(arg_name, "_p") + " = " + _render_expr(default))
            else:
                ps_params.append("$" + _safe_ident(arg_name, "_p"))
        elif isinstance(p, str):
            if p == "self":
                continue
            ps_params.append("$" + _safe_ident(p, "_p"))

    decorators = _get_list(stmt, "decorator_list")
    lines: list[str] = []
    for dec in decorators:
        if isinstance(dec, dict):
            dec_d: dict[str, object] = dec
            if _get_str(dec_d, "kind") != "Name":
                continue
            dec_name = _get_str(dec_d, "id")
            if dec_name != "":
                lines.append(indent + "# @" + dec_name)

    lines.append(indent + "function " + name + " {")
    if len(ps_params) > 0:
        lines.append(indent + "    param(" + ", ".join(ps_params) + ")")
    else:
        lines.append(indent + "    param()")

    lines.extend(_emit_body(body, indent=indent + "    ", ctx=ctx))
    lines.append(indent + "}")
    return lines


def _emit_class_def(stmt: dict[str, Any], *, indent: str, ctx: dict[str, Any]) -> list[str]:
    name = _safe_ident(_get_str(stmt, "name"), "_Cls")
    body = _get_list(stmt, "body")
    lines = [indent + "# class " + name]

    for member in body:
        if not isinstance(member, dict):
            continue
        member_d: dict[str, object] = member
        mk = _get_str(member_d, "kind")
        if mk == "FunctionDef":
            method_name = _get_str(member_d, "name")
            if method_name == "__init__":
                fn_lines = _emit_function_def(member_d, indent=indent, ctx=ctx)
                if len(fn_lines) > 0:
                    fn_lines[0] = fn_lines[0].replace("function __init__", "function " + name, 1)
                lines.extend(fn_lines)
            else:
                fn_lines = _emit_function_def(member_d, indent=indent, ctx=ctx)
                if len(fn_lines) > 0:
                    original_fn_name = "function " + _safe_ident(method_name, "_m")
                    new_fn_name = "function " + name + "_" + _safe_ident(method_name, "_m")
                    fn_lines[0] = fn_lines[0].replace(original_fn_name, new_fn_name, 1)
                lines.extend(fn_lines)
        elif mk == "AnnAssign" or mk == "Assign":
            lines.extend(_emit_stmt(member_d, indent=indent, ctx=ctx))
        elif mk == "Pass":
            pass

    return lines


# ---------------------------------------------------------------------------
# Module-level entry point
# ---------------------------------------------------------------------------

def transpile_to_powershell(east_doc: dict[str, Any]) -> str:
    """EAST ドキュメントを PowerShell コードへ変換する。"""
    if not isinstance(east_doc, dict) or _get_str(east_doc, "kind") != "Module":
        raise RuntimeError("powershell native emitter: root kind must be Module")

    body = _get_list(east_doc, "body")
    if not isinstance(body, list):
        raise RuntimeError("powershell native emitter: Module.body must be list")

    reject_backend_general_union_type_exprs(east_doc, backend_name="PowerShell backend")
    reject_backend_typed_vararg_signatures(east_doc, backend_name="PowerShell backend")

    ctx: dict[str, Any] = {}
    lines: list[str] = [
        "#Requires -Version 5.1",
        "",
        "$pytra_runtime = Join-Path $PSScriptRoot \"py_runtime.ps1\"",
        "if (Test-Path $pytra_runtime) { . $pytra_runtime }",
        "",
        "Set-StrictMode -Version Latest",
        "$ErrorActionPreference = \"Stop\"",
        "",
    ]

    # Emit module-level leading comments
    comments = _get_list(east_doc, "leading_comments")
    for c in comments:
        if isinstance(c, str):
            lines.append("# " + c)
    if len(comments) > 0:
        lines.append("")

    # Emit body
    for stmt in body:
        if isinstance(stmt, dict):
            stmt_d: dict[str, object] = stmt
            lines.extend(_emit_stmt(stmt_d, indent="", ctx=ctx))
            lines.append("")

    lines.append("if (Get-Command -Name main -ErrorAction SilentlyContinue) {")
    lines.append("    main")
    lines.append("}")
    return "\n".join(lines).rstrip() + "\n"
