"""EAST3 → TypeScript / JavaScript source code emitter.

TypeScript emitter は CommonRenderer + override 構成。
TS/JS 固有のノード（クラス、arrow function、import 等）のみ override として実装する。

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from pytra.std.json import JsonVal
from pytra.std.pathlib import Path

from toolchain2.emit.ts.types import (
    ts_type, ts_zero_value, _safe_ts_ident, _split_generic_args,
)
from toolchain2.emit.common.code_emitter import (
    RuntimeMapping, load_runtime_mapping, resolve_runtime_call,
    should_skip_module, build_import_alias_map, build_runtime_import_map,
    resolve_runtime_symbol_name,
)
from toolchain2.emit.common.common_renderer import CommonRenderer
from toolchain2.link.expand_defaults import expand_cross_module_defaults


# ---------------------------------------------------------------------------
# Emit context
# ---------------------------------------------------------------------------

@dataclass
class EmitContext:
    """Per-module mutable state during emission."""
    module_id: str = ""
    source_path: str = ""
    is_entry: bool = False
    indent_level: int = 0
    lines: list[str] = field(default_factory=list)
    strip_types: bool = False
    # Variable types in current scope
    var_types: dict[str, str] = field(default_factory=dict)
    # Current function return type
    current_return_type: str = ""
    # Runtime mapping (from mapping.json)
    mapping: RuntimeMapping = field(default_factory=RuntimeMapping)
    # Import alias → module_id map
    import_alias_modules: dict[str, str] = field(default_factory=dict)
    # Imported runtime symbols
    runtime_imports: dict[str, str] = field(default_factory=dict)
    # Class info
    class_names: set[str] = field(default_factory=set)
    class_bases: dict[str, str] = field(default_factory=dict)
    class_static_methods: dict[str, set[str]] = field(default_factory=dict)
    class_property_methods: dict[str, set[str]] = field(default_factory=dict)
    class_instance_methods: dict[str, dict[str, dict[str, JsonVal]]] = field(default_factory=dict)
    class_fields: dict[str, dict[str, str]] = field(default_factory=dict)
    enum_bases: dict[str, str] = field(default_factory=dict)
    enum_members: dict[str, dict[str, dict[str, JsonVal]]] = field(default_factory=dict)
    # Current class context
    current_class: str = ""
    # Exception type IDs
    exception_type_ids: dict[str, int] = field(default_factory=dict)
    class_type_ids: dict[str, int] = field(default_factory=dict)
    # Per-module temp counter
    temp_counter: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _indent(ctx: EmitContext) -> str:
    return "    " * ctx.indent_level


def _emit(ctx: EmitContext, line: str) -> None:
    ctx.lines.append(_indent(ctx) + line)


def _emit_blank(ctx: EmitContext) -> None:
    ctx.lines.append("")


def _next_temp(ctx: EmitContext, prefix: str) -> str:
    ctx.temp_counter += 1
    return "__" + prefix + "_" + str(ctx.temp_counter)


def _str(node: dict[str, JsonVal], key: str) -> str:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, str):
            return value
    return ""


def _bool(node: dict[str, JsonVal], key: str) -> bool:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, bool):
            return value
    return False


def _list(node: dict[str, JsonVal], key: str) -> list[JsonVal]:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, list):
            return value
    return []


def _dict(node: dict[str, JsonVal], key: str) -> dict[str, JsonVal]:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _ts_symbol_name(ctx: EmitContext, name: str) -> str:
    """Return safe TS identifier, preserving 'this' mapping for 'self'."""
    if name == "self":
        return "this"
    return _safe_ts_ident(name)


def _type_annotation(ctx: EmitContext, resolved_type: str, *, for_return: bool = False) -> str:
    """Return ': TypeAnnotation' if not in strip_types mode, else ''."""
    if ctx.strip_types:
        return ""
    if resolved_type == "" or resolved_type == "unknown":
        return ""
    tt = ts_type(resolved_type, for_return=for_return)
    if tt == "" or tt == "void" and not for_return:
        return ""
    return ": " + tt


def _return_type_annotation(ctx: EmitContext, return_type: str) -> str:
    """Return ': ReturnType' or '' for strip_types mode."""
    if ctx.strip_types:
        return ""
    if return_type == "" or return_type == "unknown":
        return ""
    tt = ts_type(return_type, for_return=True)
    if tt == "":
        return ""
    return ": " + tt


def _is_exception_type_name(ctx: EmitContext, type_name: str) -> bool:
    """Check if a type name is an exception class."""
    _BUILTIN_EXCEPTIONS: set[str] = {
        "Exception", "BaseException", "RuntimeError", "ValueError",
        "TypeError", "IndexError", "KeyError", "StopIteration",
        "AttributeError", "NameError", "NotImplementedError",
        "OverflowError", "ZeroDivisionError", "AssertionError",
        "OSError", "IOError", "FileNotFoundError", "PermissionError",
    }
    if type_name in _BUILTIN_EXCEPTIONS:
        return True
    # Check inherited from exception class
    base = ctx.class_bases.get(type_name, "")
    if base != "":
        return _is_exception_type_name(ctx, base)
    return False


def _exception_ctor_expr(type_name: str, message_code: str) -> str:
    """Build a new Error(...) expression for exception types."""
    if message_code != "":
        return "new Error(" + message_code + ")"
    return "new Error(" + '"' + type_name + '"' + ")"


# ---------------------------------------------------------------------------
# Expression rendering (used by CommonRenderer override and standalone)
# ---------------------------------------------------------------------------

def _emit_expr(ctx: EmitContext, node: JsonVal) -> str:
    """Emit an expression and return TS code string."""
    if not isinstance(node, dict):
        return "null"
    renderer = _TsExprRenderer(ctx)
    return renderer.render_expr(node)


def _emit_constant(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    value = node.get("value")
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return str(value)


def _emit_name(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    name = _str(node, "id")
    if name == "":
        name = _str(node, "repr")
    if name == "None":
        return "null"
    if name == "True":
        return "true"
    if name == "False":
        return "false"
    # Check runtime_imports for mapped names
    if name in ctx.runtime_imports:
        return ctx.runtime_imports[name]
    return _ts_symbol_name(ctx, name)


def _emit_attribute(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner_node = node.get("value")
    attr = _str(node, "attr")
    owner = _emit_expr(ctx, owner_node)
    # Handle 'self.field' → 'this.field'
    if isinstance(owner_node, dict) and _str(owner_node, "id") == "self":
        return "this." + attr
    return owner + "." + attr


def _emit_subscript(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner = _emit_expr(ctx, node.get("value"))
    slice_node = node.get("slice")
    if isinstance(slice_node, dict) and _str(slice_node, "kind") == "Slice":
        lower = slice_node.get("lower")
        upper = slice_node.get("upper")
        lower_code = _emit_expr(ctx, lower) if isinstance(lower, dict) else "0"
        upper_code = _emit_expr(ctx, upper) if isinstance(upper, dict) else "undefined"
        return owner + ".slice(" + lower_code + ", " + upper_code + ")"
    slice_code = _emit_expr(ctx, slice_node)
    return owner + "[" + slice_code + "]"


def _emit_list_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elements = _list(node, "elements")
    elem_strs = [_emit_expr(ctx, e) for e in elements]
    rt = _str(node, "resolved_type")
    elem_type = ""
    if rt.startswith("list[") and rt.endswith("]"):
        elem_type = rt[5:-1]
    if ctx.strip_types or elem_type == "":
        return "[" + ", ".join(elem_strs) + "]"
    ts_elem = ts_type(elem_type)
    return "<" + ts_elem + "[]>[" + ", ".join(elem_strs) + "]"


def _emit_dict_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    keys = _list(node, "keys")
    values = _list(node, "values")
    rt = _str(node, "resolved_type")
    pairs: list[str] = []
    for idx, key in enumerate(keys):
        kc = _emit_expr(ctx, key)
        vc = _emit_expr(ctx, values[idx]) if idx < len(values) else "null"
        pairs.append("[" + kc + ", " + vc + "]")
    if ctx.strip_types or rt == "":
        return "new Map([" + ", ".join(pairs) + "])"
    k_type = "any"
    v_type = "any"
    if rt.startswith("dict[") and rt.endswith("]"):
        parts = _split_generic_args(rt[5:-1])
        if len(parts) == 2:
            k_type = ts_type(parts[0])
            v_type = ts_type(parts[1])
    return "new Map<" + k_type + ", " + v_type + ">([" + ", ".join(pairs) + "])"


def _emit_set_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elements = _list(node, "elements")
    elem_strs = [_emit_expr(ctx, e) for e in elements]
    rt = _str(node, "resolved_type")
    if ctx.strip_types or rt == "":
        return "new Set([" + ", ".join(elem_strs) + "])"
    elem_type = "any"
    if rt.startswith("set[") and rt.endswith("]"):
        elem_type = ts_type(rt[4:-1])
    return "new Set<" + elem_type + ">([" + ", ".join(elem_strs) + "])"


def _emit_tuple_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elements = _list(node, "elements")
    elem_strs = [_emit_expr(ctx, e) for e in elements]
    return "[" + ", ".join(elem_strs) + "]"


def _emit_ifexp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    test = _emit_expr(ctx, node.get("test"))
    body = _emit_expr(ctx, node.get("body"))
    orelse = _emit_expr(ctx, node.get("orelse"))
    return "(" + test + " ? " + body + " : " + orelse + ")"


def _emit_fstring(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    values = _list(node, "values")
    parts: list[str] = []
    for v in values:
        if not isinstance(v, dict):
            continue
        vk = _str(v, "kind")
        if vk == "Constant":
            raw_val = v.get("value")
            if isinstance(raw_val, str):
                # Escape template literal
                escaped = raw_val.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                parts.append(escaped)
            continue
        if vk == "FormattedValue":
            inner = v.get("value")
            expr_code = _emit_expr(ctx, inner)
            fmt_spec = _str(v, "format_spec")
            if fmt_spec != "":
                parts.append("${" + expr_code + "}")
            else:
                parts.append("${" + expr_code + "}")
            continue
        expr_code = _emit_expr(ctx, v)
        parts.append("${" + expr_code + "}")
    return "`" + "".join(parts) + "`"


def _emit_lambda(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    arg_order = _list(node, "arg_order")
    arg_types = _dict(node, "arg_types")
    body = node.get("body")
    params: list[str] = []
    for a in arg_order:
        a_str = a if isinstance(a, str) else ""
        if ctx.strip_types:
            params.append(_safe_ts_ident(a_str))
        else:
            a_type = arg_types.get(a_str, "")
            a_type_str = a_type if isinstance(a_type, str) else ""
            ann = _type_annotation(ctx, a_type_str)
            params.append(_safe_ts_ident(a_str) + ann)
    body_code = _emit_expr(ctx, body)
    return "(" + ", ".join(params) + ") => " + body_code


def _emit_isinstance(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    obj = _emit_expr(ctx, node.get("value"))
    type_name = _str(node, "type_name")
    if type_name == "":
        type_names = _list(node, "type_names")
        if len(type_names) > 0:
            checks: list[str] = []
            for tn in type_names:
                tn_str = tn if isinstance(tn, str) else ""
                checks.append(obj + " instanceof " + _safe_ts_ident(tn_str))
            return "(" + " || ".join(checks) + ")"
    return obj + " instanceof " + _safe_ts_ident(type_name)


def _emit_unbox(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return _emit_expr(ctx, node.get("value"))


def _emit_box(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return _emit_expr(ctx, node.get("value"))


def _is_module_call(ctx: EmitContext, owner_node: JsonVal) -> bool:
    """Check if owner is a module reference."""
    if not isinstance(owner_node, dict):
        return False
    rt = _str(owner_node, "resolved_type")
    owner_id = _str(owner_node, "id")
    return rt == "module" or owner_id in ctx.import_alias_modules


def _resolve_runtime_call_name(ctx: EmitContext, node: dict[str, JsonVal], func: JsonVal) -> str:
    """Resolve a runtime_call to the mapped TS function name."""
    runtime_call = _str(node, "runtime_call")
    resolved_runtime_call = _str(node, "resolved_runtime_call")
    adapter_kind = _str(node, "runtime_call_adapter_kind")
    builtin_name = _str(node, "builtin_name")
    if builtin_name == "" and isinstance(func, dict):
        builtin_name = _str(func, "builtin_name")
    if runtime_call == "" and resolved_runtime_call != "":
        runtime_call = resolved_runtime_call
    if runtime_call == "" and isinstance(func, dict):
        runtime_call = _str(func, "runtime_call")
    name = resolve_runtime_call(runtime_call, builtin_name, adapter_kind, ctx.mapping)
    if name == "":
        name = runtime_call
    return name


def _emit_call(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    func = node.get("func")
    args = _list(node, "args")
    keywords = _list(node, "keywords")
    arg_strs = [_emit_expr(ctx, a) for a in args]
    kw_strs: list[str] = []
    for kw in keywords:
        if isinstance(kw, dict):
            kw_strs.append(_emit_expr(ctx, kw.get("value")))
    all_arg_strs = arg_strs + kw_strs

    # BuiltinCall: runtime function
    lowered = _str(node, "lowered_kind")
    if lowered == "BuiltinCall" or lowered == "RuntimeCall":
        fn_name = _resolve_runtime_call_name(ctx, node, func)
        if fn_name != "" and fn_name != "__CAST__" and fn_name != "__PANIC__":
            if fn_name == "__LIST_CTOR__":
                rt = _str(node, "resolved_type")
                if not ctx.strip_types and rt.startswith("list[") and rt.endswith("]"):
                    elem_type = ts_type(rt[5:-1])
                    return "<" + elem_type + "[]>[]"
                return "[]"
            if fn_name == "__TUPLE_CTOR__":
                return "[" + ", ".join(all_arg_strs) + "]"
            if fn_name == "__SET_CTOR__":
                rt = _str(node, "resolved_type")
                if not ctx.strip_types and rt.startswith("set[") and rt.endswith("]"):
                    elem_type = ts_type(rt[4:-1])
                    return "new Set<" + elem_type + ">([" + ", ".join(all_arg_strs) + "])"
                return "new Set([" + ", ".join(all_arg_strs) + "])"
            if fn_name == "__LIST_APPEND__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                item = arg_strs[1] if len(arg_strs) >= 2 else "null"
                return owner + ".push(" + item + ")"
            if fn_name == "__LIST_POP__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                if len(arg_strs) >= 2:
                    return owner + ".splice(" + arg_strs[1] + ", 1)[0]"
                return owner + ".pop()"
            if fn_name == "__LIST_CLEAR__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                return owner + ".length = 0"
            if fn_name == "__DICT_GET__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                key = arg_strs[1] if len(arg_strs) >= 2 else "null"
                default = arg_strs[2] if len(arg_strs) >= 3 else "null"
                return "(" + owner + ".has(" + key + ") ? " + owner + ".get(" + key + ") : " + default + ")"
            if fn_name == "__DICT_ITEMS__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                return owner + ".entries()"
            if fn_name == "__DICT_KEYS__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                return owner + ".keys()"
            if fn_name == "__DICT_VALUES__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                return owner + ".values()"
            if fn_name == "__SET_ADD__":
                owner = _emit_expr(ctx, args[0]) if len(args) >= 1 else "null"
                item = arg_strs[1] if len(arg_strs) >= 2 else "null"
                return owner + ".add(" + item + ")"
            return _safe_ts_ident(fn_name) + "(" + ", ".join(all_arg_strs) + ")"
        if fn_name == "__CAST__":
            if len(all_arg_strs) >= 1:
                return all_arg_strs[0]
            return "null"
        if fn_name == "__PANIC__":
            msg = all_arg_strs[0] if len(all_arg_strs) >= 1 else '"error"'
            return "(() => { throw new Error(" + msg + "); })()"

    if isinstance(func, dict):
        func_kind = _str(func, "kind")

        if func_kind == "Attribute":
            owner_node = func.get("value")
            attr = _str(func, "attr")
            owner_id = _str(owner_node, "id") if isinstance(owner_node, dict) else ""

            # Static method call: ClassName.method(...)
            if _str(node, "call_dispatch_kind") == "static_method":
                return _safe_ts_ident(owner_id) + "." + _safe_ts_ident(attr) + "(" + ", ".join(all_arg_strs) + ")"

            # super().__init__() → super(...)
            if isinstance(owner_node, dict) and _str(owner_node, "kind") == "Call":
                inner_func = owner_node.get("func")
                if isinstance(inner_func, dict) and _str(inner_func, "id") == "super":
                    if attr == "__init__":
                        return "super(" + ", ".join(all_arg_strs) + ")"
                    return "super." + _safe_ts_ident(attr) + "(" + ", ".join(all_arg_strs) + ")"

            # Module method call: math.sqrt etc.
            if _is_module_call(ctx, owner_node):
                mod_id = _str(node, "runtime_module_id")
                if mod_id == "":
                    mod_id = ctx.import_alias_modules.get(owner_id, "")
                runtime_symbol = _str(node, "runtime_symbol")
                if runtime_symbol == "":
                    runtime_symbol = _str(func, "runtime_symbol")
                if runtime_symbol == "":
                    runtime_symbol = attr
                if should_skip_module(mod_id, ctx.mapping):
                    resolved = resolve_runtime_symbol_name(
                        runtime_symbol,
                        ctx.mapping,
                        resolved_runtime_call=_str(node, "resolved_runtime_call"),
                        runtime_call=_str(node, "runtime_call"),
                    )
                    if resolved == "":
                        resolved = runtime_symbol
                    return _safe_ts_ident(resolved) + "(" + ", ".join(all_arg_strs) + ")"
                return _safe_ts_ident(runtime_symbol) + "(" + ", ".join(all_arg_strs) + ")"

            # Regular method call: obj.method(...)
            owner_code = _emit_expr(ctx, owner_node)
            return owner_code + "." + _safe_ts_ident(attr) + "(" + ", ".join(all_arg_strs) + ")"

        if func_kind == "Name":
            fn_id = _str(func, "id")

            # super() call
            if fn_id == "super":
                return "super(" + ", ".join(all_arg_strs) + ")"

            # Constructor call for known classes
            if fn_id in ctx.class_names:
                return "new " + _safe_ts_ident(fn_id) + "(" + ", ".join(all_arg_strs) + ")"

            # Exception constructor
            if _is_exception_type_name(ctx, fn_id):
                msg = all_arg_strs[0] if len(all_arg_strs) >= 1 else '"' + fn_id + '"'
                return "new Error(" + msg + ")"

            # runtime import
            if fn_id in ctx.runtime_imports:
                resolved = ctx.runtime_imports[fn_id]
                return _safe_ts_ident(resolved) + "(" + ", ".join(all_arg_strs) + ")"

            # Check mapping for runtime calls
            runtime_call = _str(func, "runtime_call")
            if runtime_call == "":
                runtime_call = _str(node, "runtime_call")
            if runtime_call != "":
                adapter_kind = _str(node, "runtime_call_adapter_kind")
                if adapter_kind == "":
                    adapter_kind = "builtin"
                name = resolve_runtime_call(runtime_call, fn_id, adapter_kind, ctx.mapping)
                if name != "" and name != "__CAST__":
                    return _safe_ts_ident(name) + "(" + ", ".join(all_arg_strs) + ")"

            return _safe_ts_ident(fn_id) + "(" + ", ".join(all_arg_strs) + ")"

    func_code = _emit_expr(ctx, func)
    return func_code + "(" + ", ".join(all_arg_strs) + ")"


def _emit_binop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    left = _emit_expr(ctx, node.get("left"))
    right = _emit_expr(ctx, node.get("right"))
    op = _str(node, "op")
    _OP_MAP: dict[str, str] = {
        "Add": "+", "Sub": "-", "Mult": "*", "Div": "/",
        "FloorDiv": "__floordiv", "Mod": "%", "Pow": "**",
        "BitAnd": "&", "BitOr": "|", "BitXor": "^",
        "LShift": "<<", "RShift": ">>",
    }
    op_str = _OP_MAP.get(op, op)
    if op_str == "__floordiv":
        return "pyFloorDiv(" + left + ", " + right + ")"
    return "(" + left + " " + op_str + " " + right + ")"


def _emit_unaryop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    operand = _emit_expr(ctx, node.get("operand"))
    op = _str(node, "op")
    _OP_MAP: dict[str, str] = {"USub": "-", "UAdd": "+", "Not": "!", "Invert": "~"}
    op_str = _OP_MAP.get(op, op)
    return "(" + op_str + operand + ")"


def _emit_compare(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    left = _emit_expr(ctx, node.get("left"))
    comparators = _list(node, "comparators")
    ops = _list(node, "ops")
    if len(comparators) == 0 or len(ops) == 0:
        return left
    _OP_MAP: dict[str, str] = {
        "Eq": "===", "NotEq": "!==",
        "Lt": "<", "LtE": "<=", "Gt": ">", "GtE": ">=",
        "Is": "===", "IsNot": "!==",
        "In": "__IN__", "NotIn": "__NOT_IN__",
    }
    parts: list[str] = []
    current_left = left
    for idx, comparator in enumerate(comparators):
        op_obj = ops[idx] if idx < len(ops) else None
        op_name = op_obj if isinstance(op_obj, str) else _str(op_obj, "kind") if isinstance(op_obj, dict) else ""
        op_text = _OP_MAP.get(op_name, op_name)
        right = _emit_expr(ctx, comparator)
        if op_text == "__IN__":
            parts.append("pyIn(" + current_left + ", " + right + ")")
        elif op_text == "__NOT_IN__":
            parts.append("(!pyIn(" + current_left + ", " + right + "))")
        else:
            parts.append("(" + current_left + " " + op_text + " " + right + ")")
        current_left = right
    if len(parts) == 1:
        return parts[0]
    return "(" + " && ".join(parts) + ")"


def _emit_boolop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    values = _list(node, "values")
    op = _str(node, "op")
    op_text = "&&" if op == "And" else "||"
    return "(" + (" " + op_text + " ").join(_emit_expr(ctx, v) for v in values) + ")"


# ---------------------------------------------------------------------------
# CommonRenderer subclasses
# ---------------------------------------------------------------------------

class _TsExprRenderer(CommonRenderer):
    def __init__(self, ctx: EmitContext) -> None:
        self.ctx = ctx
        super().__init__("ts")

    def render_name(self, node: dict[str, JsonVal]) -> str:
        return _emit_name(self.ctx, node)

    def render_constant(self, node: dict[str, JsonVal]) -> str:
        return _emit_constant(self.ctx, node)

    def render_binop(self, node: dict[str, JsonVal]) -> str:
        return _emit_binop(self.ctx, node)

    def render_unaryop(self, node: dict[str, JsonVal]) -> str:
        return _emit_unaryop(self.ctx, node)

    def render_compare(self, node: dict[str, JsonVal]) -> str:
        return _emit_compare(self.ctx, node)

    def render_boolop(self, node: dict[str, JsonVal]) -> str:
        return _emit_boolop(self.ctx, node)

    def render_attribute(self, node: dict[str, JsonVal]) -> str:
        return _emit_attribute(self.ctx, node)

    def render_call(self, node: dict[str, JsonVal]) -> str:
        return _emit_call(self.ctx, node)

    def render_assign_stmt(self, node: dict[str, JsonVal]) -> str:
        raise RuntimeError("ts expr renderer does not handle assign")

    def render_expr_extension(self, node: dict[str, JsonVal]) -> str:
        return _emit_expr_extension(self.ctx, node)


class _TsStmtRenderer(CommonRenderer):
    def __init__(self, ctx: EmitContext) -> None:
        self.ctx = ctx
        super().__init__("ts")
        self.state.lines = ctx.lines
        self.state.indent_level = ctx.indent_level

    def render_name(self, node: dict[str, JsonVal]) -> str:
        return _emit_name(self.ctx, node)

    def render_constant(self, node: dict[str, JsonVal]) -> str:
        return _emit_constant(self.ctx, node)

    def render_expr(self, node: JsonVal) -> str:
        return _emit_expr(self.ctx, node)

    def render_attribute(self, node: dict[str, JsonVal]) -> str:
        return _emit_attribute(self.ctx, node)

    def render_call(self, node: dict[str, JsonVal]) -> str:
        return _emit_call(self.ctx, node)

    def render_assign_stmt(self, node: dict[str, JsonVal]) -> str:
        raise RuntimeError("ts stmt renderer assign not used as string")

    def emit_assign_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        kind = self._str(node, "kind")
        if kind == "AnnAssign":
            _emit_ann_assign(self.ctx, node)
        else:
            _emit_assign(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def emit_return_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_return(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def emit_expr_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_expr_stmt(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def emit_raise_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_raise(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def render_raise_value(self, node: dict[str, JsonVal]) -> str:
        raise RuntimeError("ts stmt renderer raise value not used directly")

    def render_except_open(self, handler: dict[str, JsonVal]) -> str:
        name = _str(handler, "name")
        if name != "":
            return "} catch (" + _safe_ts_ident(name) + ") {"
        return "} catch (e) {"

    def emit_try_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_try(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def emit_stmt(self, node: JsonVal) -> None:
        _COMMON_KINDS: set[str] = {"Expr", "Return", "Assign", "AnnAssign", "Pass", "Raise", "Try", "comment", "blank", "If", "While"}
        if isinstance(node, dict):
            kind = self._str(node, "kind")
            if kind in _COMMON_KINDS:
                super().emit_stmt(node)
                self.ctx.indent_level = self.state.indent_level
                return
        if isinstance(node, dict):
            self.emit_stmt_extension(node)

    def emit_stmt_extension(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_stmt(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level


def _emit_common_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> bool:
    _COMMON_KINDS: set[str] = {"Expr", "Return", "Assign", "AnnAssign", "Pass", "Raise", "Try", "comment", "blank", "If", "While"}
    kind = _str(node, "kind")
    if kind not in _COMMON_KINDS:
        return False
    renderer = _TsStmtRenderer(ctx)
    renderer.emit_stmt(node)
    ctx.indent_level = renderer.state.indent_level
    return True


# ---------------------------------------------------------------------------
# Expression extensions
# ---------------------------------------------------------------------------

def _emit_expr_extension(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    kind = _str(node, "kind")
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
        inner = node.get("value")
        return _emit_expr(ctx, inner)
    if kind == "Lambda":
        return _emit_lambda(ctx, node)
    if kind == "IsInstance":
        return _emit_isinstance(ctx, node)
    if kind == "Unbox":
        return _emit_unbox(ctx, node)
    if kind == "Box":
        return _emit_box(ctx, node)
    if kind == "ObjStr":
        arg = node.get("value")
        return "pyStr(" + _emit_expr(ctx, arg) + ")"
    if kind == "ObjLen":
        arg = node.get("value")
        return "pyLen(" + _emit_expr(ctx, arg) + ")"
    if kind == "ObjBool":
        arg = node.get("value")
        return "pyBool(" + _emit_expr(ctx, arg) + ")"
    if kind == "ObjTypeId":
        arg = node.get("value")
        return "pyTypeId(" + _emit_expr(ctx, arg) + ")"
    if kind == "IsSubtype":
        actual = _emit_expr(ctx, node.get("actual_type_id"))
        expected = _emit_expr(ctx, node.get("expected_type_id"))
        return "pyIsSubtype(" + actual + ", " + expected + ")"
    if kind == "IsSubclass":
        actual = _emit_expr(ctx, node.get("actual_type_id"))
        expected = _emit_expr(ctx, node.get("expected_type_id"))
        return "pyIsSubtype(" + actual + ", " + expected + ")"
    if kind == "CovariantCopy":
        return _emit_expr(ctx, node.get("value"))
    if kind == "ListComp":
        return _emit_list_comp(ctx, node)
    if kind == "SetComp":
        return _emit_set_comp(ctx, node)
    if kind == "DictComp":
        return _emit_dict_comp(ctx, node)
    if kind == "Slice":
        # Bare slice — not in subscript context
        lower = node.get("lower")
        upper = node.get("upper")
        lc = _emit_expr(ctx, lower) if isinstance(lower, dict) else "null"
        uc = _emit_expr(ctx, upper) if isinstance(upper, dict) else "null"
        return "pySlice(__obj__, " + lc + ", " + uc + ")"
    raise RuntimeError("unsupported_expr_kind_ts: " + kind)


def _emit_list_comp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elt = _emit_expr(ctx, node.get("elt"))
    generators = _list(node, "generators")
    if len(generators) == 0:
        return "[" + elt + "]"
    gen = generators[0]
    if not isinstance(gen, dict):
        return "[" + elt + "]"
    iter_code = _emit_expr(ctx, gen.get("iter"))
    target_node = gen.get("target")
    target_code = _emit_expr(ctx, target_node) if isinstance(target_node, dict) else "_item"
    return iter_code + ".map((" + target_code + ") => " + elt + ")"


def _emit_set_comp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elt = _emit_expr(ctx, node.get("elt"))
    generators = _list(node, "generators")
    if len(generators) == 0:
        return "new Set([" + elt + "])"
    gen = generators[0]
    if not isinstance(gen, dict):
        return "new Set([" + elt + "])"
    iter_code = _emit_expr(ctx, gen.get("iter"))
    target_node = gen.get("target")
    target_code = _emit_expr(ctx, target_node) if isinstance(target_node, dict) else "_item"
    return "new Set(" + iter_code + ".map((" + target_code + ") => " + elt + "))"


def _emit_dict_comp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    key = _emit_expr(ctx, node.get("key"))
    value = _emit_expr(ctx, node.get("value"))
    generators = _list(node, "generators")
    if len(generators) == 0:
        return "new Map([[" + key + ", " + value + "]])"
    gen = generators[0]
    if not isinstance(gen, dict):
        return "new Map([[" + key + ", " + value + "]])"
    iter_code = _emit_expr(ctx, gen.get("iter"))
    target_node = gen.get("target")
    target_code = _emit_expr(ctx, target_node) if isinstance(target_node, dict) else "_item"
    return "new Map(" + iter_code + ".map((" + target_code + ") => [" + key + ", " + value + "]))"


# ---------------------------------------------------------------------------
# Statement emission
# ---------------------------------------------------------------------------

def _emit_expr_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    value = node.get("value")
    if not isinstance(value, dict):
        return
    vk = _str(value, "kind")
    # String constant at statement level → docstring/comment
    if vk == "Constant" and isinstance(value.get("value"), str):
        doc_text = value.get("value")
        if isinstance(doc_text, str) and doc_text.strip() != "":
            for line in doc_text.strip().split("\n"):
                _emit(ctx, "// " + line)
        return
    _emit(ctx, _emit_expr(ctx, value) + ";")


def _emit_ann_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target_val = node.get("target")
    rt = _str(node, "decl_type")
    if rt == "":
        rt = _str(node, "resolved_type")
    value = node.get("value")

    # Attribute assignment (self.x = ...)
    is_attr_target = isinstance(target_val, dict) and _str(target_val, "kind") == "Attribute"
    if is_attr_target:
        lhs = _emit_expr(ctx, target_val)
        if value is not None:
            _emit(ctx, lhs + " = " + _emit_expr(ctx, value) + ";")
        return

    # Get target name
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

    name = _ts_symbol_name(ctx, target_name)
    is_reassign = _bool(node, "is_reassign") or name in ctx.var_types
    ann = _type_annotation(ctx, rt)

    if value is not None:
        val_code = _emit_expr(ctx, value)
        if is_reassign:
            _emit(ctx, name + " = " + val_code + ";")
        else:
            ctx.var_types[name] = rt
            # Use const if arg_usage says readonly, otherwise let
            kw = "const" if _bool(node, "arg_usage_readonly") else "let"
            _emit(ctx, kw + " " + name + ann + " = " + val_code + ";")
    else:
        if not is_reassign:
            ctx.var_types[name] = rt
            zero = ts_zero_value(rt)
            _emit(ctx, "let " + name + ann + " = " + zero + ";")


def _emit_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    targets = _list(node, "targets")
    value = node.get("value")
    target_single = node.get("target")
    if len(targets) == 0 and isinstance(target_single, dict):
        targets = [target_single]
    if len(targets) == 0:
        return

    val_code = _emit_expr(ctx, value)
    target_node = targets[0]

    if isinstance(target_node, dict):
        t_kind = _str(target_node, "kind")
        if t_kind in ("Name", "NameTarget"):
            name_raw = _str(target_node, "id")
            if name_raw == "":
                name_raw = _str(target_node, "repr")
            name = _ts_symbol_name(ctx, name_raw)
            if name == "_":
                _emit(ctx, "void (" + val_code + ");")
                return
            if name in ctx.var_types:
                _emit(ctx, name + " = " + val_code + ";")
            else:
                decl_type = _str(node, "decl_type")
                if decl_type == "" or decl_type == "unknown":
                    decl_type = _str(target_node, "resolved_type")
                if decl_type == "" or decl_type == "unknown":
                    decl_type = _str(value, "resolved_type") if isinstance(value, dict) else ""
                ctx.var_types[name] = decl_type
                ann = _type_annotation(ctx, decl_type)
                kw = "const" if _bool(node, "declare_const") else "let"
                _emit(ctx, kw + " " + name + ann + " = " + val_code + ";")
            return
        if t_kind == "Attribute":
            lhs = _emit_expr(ctx, target_node)
            _emit(ctx, lhs + " = " + val_code + ";")
            return
        if t_kind == "Subscript":
            lhs = _emit_expr(ctx, target_node)
            _emit(ctx, lhs + " = " + val_code + ";")
            return

    _emit(ctx, _emit_expr(ctx, target_node) + " = " + val_code + ";")


def _emit_aug_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target = _emit_expr(ctx, node.get("target"))
    value = _emit_expr(ctx, node.get("value"))
    op = _str(node, "op")
    _AUG_OP: dict[str, str] = {
        "Add": "+=", "Sub": "-=", "Mult": "*=", "Div": "/=",
        "Mod": "%=", "Pow": "**=",
        "BitAnd": "&=", "BitOr": "|=", "BitXor": "^=",
        "LShift": "<<=", "RShift": ">>=",
    }
    op_str = _AUG_OP.get(op, op + "=")
    if op == "FloorDiv":
        _emit(ctx, target + " = pyFloorDiv(" + target + ", " + value + ");")
    else:
        _emit(ctx, target + " " + op_str + " " + value + ";")


def _emit_return(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    value = node.get("value")
    if value is not None and isinstance(value, dict):
        _emit(ctx, "return " + _emit_expr(ctx, value) + ";")
    else:
        _emit(ctx, "return;")


def _emit_raise(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    exc = node.get("exc")
    if exc is None:
        exc = node.get("value")
    if exc is not None and isinstance(exc, dict):
        exc_code = _emit_expr(ctx, exc)
        exc_type = _str(exc, "resolved_type")
        # If it looks like a constructor call, wrap in new Error
        if _str(exc, "kind") == "Call":
            func = exc.get("func")
            func_name = _str(func, "id") if isinstance(func, dict) else ""
            if _is_exception_type_name(ctx, func_name):
                args = _list(exc, "args")
                arg_strs = [_emit_expr(ctx, a) for a in args]
                msg = arg_strs[0] if len(arg_strs) >= 1 else '"' + func_name + '"'
                _emit(ctx, "throw new Error(" + msg + ");")
                return
        _emit(ctx, "throw " + exc_code + ";")
    else:
        _emit(ctx, "throw new Error(\"unknown error\");")


def _emit_try(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    body = _list(node, "body")
    handlers = _list(node, "handlers")
    finalbody = _list(node, "finalbody")

    _emit(ctx, "try {")
    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1

    for raw_handler in handlers:
        if not isinstance(raw_handler, dict):
            continue
        name = _str(raw_handler, "name")
        if name != "":
            _emit(ctx, "} catch (" + _safe_ts_ident(name) + ") {")
        else:
            _emit(ctx, "} catch (e) {")
        ctx.indent_level += 1
        _emit_body(ctx, _list(raw_handler, "body"))
        ctx.indent_level -= 1

    if len(finalbody) > 0:
        _emit(ctx, "} finally {")
        ctx.indent_level += 1
        _emit_body(ctx, finalbody)
        ctx.indent_level -= 1

    _emit(ctx, "}")


def _emit_var_decl(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name_raw = _str(node, "name")
    name = _ts_symbol_name(ctx, name_raw)
    rt = _str(node, "resolved_type")
    value = node.get("value")
    ann = _type_annotation(ctx, rt)
    if value is not None:
        _emit(ctx, "let " + name + ann + " = " + _emit_expr(ctx, value) + ";")
    else:
        zero = ts_zero_value(rt)
        _emit(ctx, "let " + name + ann + " = " + zero + ";")
    ctx.var_types[name] = rt


def _emit_swap(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    a = _emit_expr(ctx, node.get("a"))
    b = _emit_expr(ctx, node.get("b"))
    tmp = _next_temp(ctx, "swap")
    ann = _type_annotation(ctx, _str(node, "resolved_type"))
    _emit(ctx, "let " + tmp + ann + " = " + a + ";")
    _emit(ctx, a + " = " + b + ";")
    _emit(ctx, b + " = " + tmp + ";")


def _emit_multi_assign(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    # MultiAssign: a, b = expr — unpack a tuple
    targets = _list(node, "targets")
    value = node.get("value")
    val_code = _emit_expr(ctx, value)
    tmp = _next_temp(ctx, "tup")
    rt = _str(node, "resolved_type") if isinstance(node, dict) else ""
    val_rt = _str(value, "resolved_type") if isinstance(value, dict) else ""
    if rt == "":
        rt = val_rt
    ann = _type_annotation(ctx, rt)
    _emit(ctx, "const " + tmp + ann + " = " + val_code + ";")
    for idx, target in enumerate(targets):
        if not isinstance(target, dict):
            continue
        t_kind = _str(target, "kind")
        if t_kind in ("Name", "NameTarget"):
            name_raw = _str(target, "id")
            if name_raw == "":
                name_raw = _str(target, "repr")
            name = _ts_symbol_name(ctx, name_raw)
            t_rt = _str(target, "resolved_type")
            t_ann = _type_annotation(ctx, t_rt)
            if name in ctx.var_types:
                _emit(ctx, name + " = " + tmp + "[" + str(idx) + "];")
            else:
                ctx.var_types[name] = t_rt
                _emit(ctx, "let " + name + t_ann + " = " + tmp + "[" + str(idx) + "];")


def _emit_for_core(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target_node = node.get("target")
    iter_node = node.get("iter")
    body = _list(node, "body")
    orelse = _list(node, "orelse")

    target_code = _emit_expr(ctx, target_node) if isinstance(target_node, dict) else "_item"
    iter_code = _emit_expr(ctx, iter_node) if isinstance(iter_node, dict) else "[]"

    _emit(ctx, "for (const " + target_code + " of " + iter_code + ") {")
    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")
    if len(orelse) > 0:
        _emit_body(ctx, orelse)


def _emit_static_range_for(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    """StaticRangeForPlan: for i in range(start, stop, step) — emit as C-style for loop."""
    target_node = node.get("target")
    start_node = node.get("start")
    stop_node = node.get("stop")
    step_node = node.get("step")
    body = _list(node, "body")

    target_code = _emit_expr(ctx, target_node) if isinstance(target_node, dict) else "_i"
    target_rt = _str(target_node, "resolved_type") if isinstance(target_node, dict) else "int64"
    ann = _type_annotation(ctx, target_rt)
    start_code = _emit_expr(ctx, start_node) if isinstance(start_node, dict) else "0"
    stop_code = _emit_expr(ctx, stop_node) if isinstance(stop_node, dict) else "0"
    step_code = _emit_expr(ctx, step_node) if isinstance(step_node, dict) else "1"
    step_is_one = isinstance(step_node, dict) and _str(step_node, "kind") == "Constant" and step_node.get("value") == 1

    # Register loop variable in var_types
    if isinstance(target_node, dict):
        name = _str(target_node, "id")
        if name != "":
            ctx.var_types[_ts_symbol_name(ctx, name)] = target_rt

    if step_is_one:
        _emit(ctx, "for (let " + target_code + ann + " = " + start_code + "; " + target_code + " < " + stop_code + "; " + target_code + "++) {")
    else:
        _emit(ctx, "for (let " + target_code + ann + " = " + start_code + "; " + target_code + " < " + stop_code + "; " + target_code + " += " + step_code + ") {")
    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_runtime_iter_for(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    """RuntimeIterForPlan: for x in container."""
    target_node = node.get("target")
    iter_node = node.get("iter")
    body = _list(node, "body")

    target_code = _emit_expr(ctx, target_node) if isinstance(target_node, dict) else "_item"
    target_rt = _str(target_node, "resolved_type") if isinstance(target_node, dict) else ""
    if isinstance(target_node, dict):
        name = _str(target_node, "id")
        if name != "":
            ctx.var_types[_ts_symbol_name(ctx, name)] = target_rt
    iter_code = _emit_expr(ctx, iter_node) if isinstance(iter_node, dict) else "[]"

    _emit(ctx, "for (const " + target_code + " of " + iter_code + ") {")
    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_with(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    """With statement → try/finally."""
    items = _list(node, "items")
    body = _list(node, "body")
    ctx_vars: list[tuple[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        ctx_expr = item.get("context_expr")
        opt_var = item.get("optional_vars")
        ctx_code = _emit_expr(ctx, ctx_expr) if isinstance(ctx_expr, dict) else "null"
        var_name = ""
        if isinstance(opt_var, dict):
            var_name = _ts_symbol_name(ctx, _str(opt_var, "id"))
        ctx_vars.append((ctx_code, var_name))

    for ctx_code, var_name in ctx_vars:
        if var_name != "":
            ann = ""
            _emit(ctx, "const " + var_name + ann + " = " + ctx_code + ";")
        else:
            _emit(ctx, ctx_code + ";")
    _emit(ctx, "try {")
    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "} finally {")
    ctx.indent_level += 1
    for _, var_name in ctx_vars:
        if var_name != "":
            _emit(ctx, var_name + ".close();")
    ctx.indent_level -= 1
    _emit(ctx, "}")


def _emit_type_alias(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    rt = _str(node, "value_type")
    if rt == "" or ctx.strip_types:
        return
    tt = ts_type(rt)
    _emit(ctx, "type " + _safe_ts_ident(name) + " = " + tt + ";")
    _emit_blank(ctx)


def _emit_break(ctx: EmitContext) -> None:
    _emit(ctx, "break;")


def _emit_continue(ctx: EmitContext) -> None:
    _emit(ctx, "continue;")


def _emit_stmt(ctx: EmitContext, node: JsonVal) -> None:
    if not isinstance(node, dict):
        return
    if _emit_common_stmt(ctx, node):
        return
    kind = _str(node, "kind")
    if kind == "AugAssign":
        _emit_aug_assign(ctx, node)
    elif kind == "ForCore":
        _emit_for_core(ctx, node)
    elif kind == "RuntimeIterForPlan":
        _emit_runtime_iter_for(ctx, node)
    elif kind == "StaticRangeForPlan":
        _emit_static_range_for(ctx, node)
    elif kind == "FunctionDef" or kind == "ClosureDef":
        _emit_function_def(ctx, node)
    elif kind == "ClassDef":
        _emit_class_def(ctx, node)
    elif kind in ("ImportFrom", "Import"):
        _emit_import_stmt(ctx, node)
    elif kind == "VarDecl":
        _emit_var_decl(ctx, node)
    elif kind == "Swap":
        _emit_swap(ctx, node)
    elif kind in ("MultiAssign", "TupleUnpack"):
        _emit_multi_assign(ctx, node)
    elif kind == "With":
        _emit_with(ctx, node)
    elif kind == "TypeAlias":
        _emit_type_alias(ctx, node)
    elif kind == "Break":
        _emit_break(ctx)
    elif kind == "Continue":
        _emit_continue(ctx)
    elif kind == "ErrorReturn":
        # native_throw style: no-op (errors are thrown, not returned)
        pass
    elif kind == "ErrorCheck":
        pass
    elif kind == "ErrorCatch":
        pass
    elif kind == "comment":
        text = _str(node, "text")
        if text != "":
            _emit(ctx, "// " + text)
    elif kind == "blank":
        _emit_blank(ctx)
    else:
        raise RuntimeError("unsupported_stmt_kind_ts: " + kind)


def _emit_body(ctx: EmitContext, body: list[JsonVal]) -> None:
    for stmt in body:
        _emit_stmt(ctx, stmt)


# ---------------------------------------------------------------------------
# Import emission
# ---------------------------------------------------------------------------

def _emit_import_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    """Emit an import statement as an ES module import or skip for runtime modules."""
    kind = _str(node, "kind")
    if kind == "ImportFrom":
        module = _str(node, "module")
        if should_skip_module(module, ctx.mapping):
            return
        if module.startswith("typing") or module.startswith("__future__") or module.startswith("dataclasses"):
            return
        names = _list(node, "names")
        imported: list[str] = []
        for nm in names:
            if not isinstance(nm, dict):
                continue
            name = _str(nm, "name")
            asname = _str(nm, "asname")
            if name == "" or name == "*":
                continue
            if asname != "":
                imported.append(name + " as " + _safe_ts_ident(asname))
            else:
                imported.append(_safe_ts_ident(name))
        if len(imported) == 0:
            return
        mod_path = _module_id_to_path(module)
        ext = "" if ctx.strip_types else ""
        _emit(ctx, "import { " + ", ".join(imported) + " } from \"" + mod_path + ext + "\";")
    elif kind == "Import":
        names = _list(node, "names")
        for nm in names:
            if not isinstance(nm, dict):
                continue
            name = _str(nm, "name")
            asname = _str(nm, "asname")
            if name == "":
                continue
            if should_skip_module(name, ctx.mapping):
                continue
            mod_path = _module_id_to_path(name)
            local = _safe_ts_ident(asname if asname != "" else name.rsplit(".", 1)[-1])
            _emit(ctx, "import * as " + local + " from \"" + mod_path + "\";")


def _module_id_to_path(module_id: str) -> str:
    """Convert a module ID like 'pytra.std.math' to a relative import path."""
    parts = module_id.split(".")
    return "./" + "/".join(parts)


# ---------------------------------------------------------------------------
# Function definition emission
# ---------------------------------------------------------------------------

def _emit_function_def(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    arg_types = _dict(node, "arg_types")
    arg_order = _list(node, "arg_order")
    return_type = _str(node, "return_type")
    body = _list(node, "body")
    decorators = _list(node, "decorators")
    is_closure = _str(node, "kind") == "ClosureDef"

    # Skip extern declarations
    for d in decorators:
        if isinstance(d, str) and d == "extern":
            return

    is_staticmethod = False
    is_classmethod = False
    is_property = False
    for d in decorators:
        if isinstance(d, str):
            if d == "staticmethod":
                is_staticmethod = True
            elif d == "classmethod":
                is_classmethod = True
            elif d == "property":
                is_property = True

    fn_name = _safe_ts_ident(name)
    saved_vars = dict(ctx.var_types)
    saved_ret = ctx.current_return_type
    ctx.current_return_type = return_type

    # Build parameter list
    params: list[str] = []
    for a in arg_order:
        a_str = a if isinstance(a, str) else ""
        if a_str == "self" or a_str == "cls":
            continue
        a_type_val = arg_types.get(a_str, "")
        a_type = a_type_val if isinstance(a_type_val, str) else ""
        safe_a = _safe_ts_ident(a_str)
        ctx.var_types[safe_a] = a_type
        ann = _type_annotation(ctx, a_type)
        params.append(safe_a + ann)

    # Return type annotation
    ret_ann = _return_type_annotation(ctx, return_type)

    # Method in class context
    if ctx.current_class != "" and not is_staticmethod and not is_classmethod:
        if is_property:
            _emit(ctx, "get " + fn_name + "()" + ret_ann + " {")
        else:
            _emit(ctx, fn_name + "(" + ", ".join(params) + ")" + ret_ann + " {")
    elif ctx.current_class != "" and is_staticmethod:
        _emit(ctx, "static " + fn_name + "(" + ", ".join(params) + ")" + ret_ann + " {")
    elif ctx.current_class != "" and is_classmethod:
        _emit(ctx, "static " + fn_name + "(" + ", ".join(params) + ")" + ret_ann + " {")
    elif is_closure:
        # ClosureDef: arrow function assigned to variable
        _emit(ctx, "const " + fn_name + " = (" + ", ".join(params) + ")" + ret_ann + " => {")
    else:
        _emit(ctx, "function " + fn_name + "(" + ", ".join(params) + ")" + ret_ann + " {")

    ctx.indent_level += 1
    _emit_body(ctx, body)
    ctx.indent_level -= 1
    _emit(ctx, "}")
    if ctx.current_class == "":
        _emit_blank(ctx)

    ctx.var_types = saved_vars
    ctx.current_return_type = saved_ret


# ---------------------------------------------------------------------------
# Class definition emission
# ---------------------------------------------------------------------------

def _collect_class_fields(ctx: EmitContext, node: dict[str, JsonVal]) -> list[tuple[str, str]]:
    """Collect class fields from field_types or __init__ body."""
    fields: list[tuple[str, str]] = []
    field_types = _dict(node, "field_types")
    if len(field_types) > 0:
        for fname, ftype in field_types.items():
            if isinstance(fname, str) and isinstance(ftype, str) and fname != "":
                fields.append((fname, ftype))
        return fields
    # Scan AnnAssign in class body (dataclass style)
    is_dataclass = _bool(node, "dataclass")
    body = _list(node, "body")
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
            if ft_name != "" and frt != "":
                fields.append((ft_name, frt))
    return fields


def _emit_class_def(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    base = _str(node, "base")
    body = _list(node, "body")
    is_dataclass = _bool(node, "dataclass")

    ctx.class_names.add(name)
    if base != "":
        ctx.class_bases[name] = base

    # Check for enum
    enum_base = ctx.enum_bases.get(name, "")
    if enum_base in ("Enum", "IntEnum", "IntFlag"):
        _emit_enum_class(ctx, node, name)
        return

    fields = _collect_class_fields(ctx, node)

    # Collect static/instance methods in first pass
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        sk = _str(stmt, "kind")
        if sk not in ("FunctionDef", "ClosureDef"):
            continue
        mname = _str(stmt, "name")
        decorators = _list(stmt, "decorators")
        is_static = False
        for d in decorators:
            if isinstance(d, str) and d == "staticmethod":
                is_static = True
                break
        if is_static:
            ctx.class_static_methods.setdefault(name, set()).add(mname)
        else:
            ctx.class_instance_methods.setdefault(name, {})[mname] = stmt

    # Save class context
    saved_class = ctx.current_class
    ctx.current_class = name

    # Emit class declaration
    extends = " extends " + _safe_ts_ident(base) if base != "" and not _is_exception_type_name(ctx, name) else ""
    if _is_exception_type_name(ctx, name):
        extends = " extends Error"
    _emit(ctx, "class " + _safe_ts_ident(name) + extends + " {")
    ctx.indent_level += 1

    # Emit field declarations (non-dataclass or explicit fields)
    if not ctx.strip_types and len(fields) > 0:
        for fname, ftype in fields:
            ann = _type_annotation(ctx, ftype)
            _emit(ctx, fname + ann + ";")
        _emit_blank(ctx)

    # Emit body (methods, AnnAssign at class level)
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        sk = _str(stmt, "kind")
        if sk in ("FunctionDef", "ClosureDef"):
            _emit_function_def(ctx, stmt)
        elif sk == "AnnAssign" and is_dataclass:
            # Skip - fields already emitted above
            pass
        elif sk in ("comment", "blank"):
            _emit_stmt(ctx, stmt)
        elif sk == "ClassDef":
            _emit_class_def(ctx, stmt)
        elif sk == "Pass":
            pass
        else:
            _emit_stmt(ctx, stmt)

    ctx.indent_level -= 1
    _emit(ctx, "}")
    _emit_blank(ctx)

    ctx.current_class = saved_class


def _emit_enum_class(ctx: EmitContext, node: dict[str, JsonVal], name: str) -> None:
    enum_members = ctx.enum_members.get(name, {})
    body = _list(node, "body")

    _emit(ctx, "const " + _safe_ts_ident(name) + " = {")
    ctx.indent_level += 1
    # Collect member assignments from body
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        sk = _str(stmt, "kind")
        if sk in ("AnnAssign", "Assign"):
            target = stmt.get("target")
            value = stmt.get("value")
            member_name = ""
            if isinstance(target, dict):
                member_name = _str(target, "id")
            elif isinstance(target, str):
                member_name = target
            if member_name != "" and isinstance(value, dict):
                val_code = _emit_expr(ctx, value)
                _emit(ctx, _safe_ts_ident(member_name) + ": " + val_code + ",")
    ctx.indent_level -= 1
    _emit(ctx, "} as const;")
    _emit(ctx, "type " + _safe_ts_ident(name) + " = typeof " + _safe_ts_ident(name) + "[keyof typeof " + _safe_ts_ident(name) + "];")
    _emit_blank(ctx)


# ---------------------------------------------------------------------------
# Module-level emission
# ---------------------------------------------------------------------------

def _collect_module_class_info(ctx: EmitContext, body: list[JsonVal]) -> None:
    """First pass: collect all class names, bases, enum types, and method info."""
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        sk = _str(stmt, "kind")
        if sk == "ClassDef":
            class_name = _str(stmt, "name")
            ctx.class_names.add(class_name)
            base = _str(stmt, "base")
            if base != "":
                ctx.class_bases[class_name] = base
            if base in ("Enum", "IntEnum", "IntFlag"):
                ctx.enum_bases[class_name] = base
            field_types = _dict(stmt, "field_types")
            class_fields: dict[str, str] = {}
            for fname, ftype in field_types.items():
                if isinstance(fname, str) and isinstance(ftype, str):
                    class_fields[fname] = ftype
            ctx.class_fields[class_name] = class_fields
            # Collect enum members
            enum_members: dict[str, dict[str, JsonVal]] = {}
            for sub_stmt in _list(stmt, "body"):
                if not isinstance(sub_stmt, dict):
                    continue
                sub_sk = _str(sub_stmt, "kind")
                if sub_sk in ("AnnAssign", "Assign"):
                    target = sub_stmt.get("target")
                    mname = ""
                    if isinstance(target, dict):
                        mname = _str(target, "id")
                    elif isinstance(target, str):
                        mname = target
                    if mname != "":
                        enum_members[mname] = sub_stmt
            ctx.enum_members[class_name] = enum_members


def _emit_module_header(ctx: EmitContext, body: list[JsonVal]) -> None:
    """Emit top-level import statements."""
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        kind = _str(stmt, "kind")
        if kind in ("ImportFrom", "Import"):
            _emit_import_stmt(ctx, stmt)


def emit_ts_module(east3_doc: dict[str, JsonVal], *, strip_types: bool = False) -> str:
    """Emit a complete TypeScript (or JavaScript) source file from an EAST3 document.

    Args:
        east3_doc: linked EAST3 JSON dict with meta.linked_program_v1.
        strip_types: If True, emit JavaScript (no type annotations).

    Returns:
        TypeScript/JavaScript source code string, or empty string if module should be skipped.
    """
    meta = _dict(east3_doc, "meta")
    module_id = ""

    emit_ctx_meta = _dict(meta, "emit_context")
    if emit_ctx_meta:
        module_id = _str(emit_ctx_meta, "module_id")
    if module_id == "":
        module_id = _str(meta, "module_id")
    lp = _dict(meta, "linked_program_v1")
    if module_id == "" and lp:
        module_id = _str(lp, "module_id")

    if module_id != "":
        expand_cross_module_defaults([(module_id, east3_doc)])

    # Load runtime mapping
    mapping_path = Path(__file__).resolve().parents[3] / "runtime" / "ts" / "mapping.json"
    mapping = load_runtime_mapping(mapping_path)

    # Skip runtime modules
    if should_skip_module(module_id, mapping):
        return ""

    ctx = EmitContext(
        module_id=module_id,
        source_path=_str(east3_doc, "source_path"),
        is_entry=_bool(emit_ctx_meta, "is_entry") if emit_ctx_meta else False,
        strip_types=strip_types,
        mapping=mapping,
    )

    body = _list(east3_doc, "body")
    main_guard = _list(east3_doc, "main_guard_body")

    # Collect type info from linked_program_v1
    if len(lp) > 0:
        type_info_table = _dict(lp, "type_info_table_v1")
        for fqcn, info in type_info_table.items():
            if not isinstance(fqcn, str) or not isinstance(info, dict):
                continue
            type_id_val = info.get("id")
            if isinstance(type_id_val, int):
                ctx.exception_type_ids[fqcn] = type_id_val
                ctx.class_type_ids[fqcn] = type_id_val

    ctx.import_alias_modules = build_import_alias_map(meta)
    ctx.runtime_imports = build_runtime_import_map(meta, mapping)

    # First pass: collect class info
    _collect_module_class_info(ctx, body)

    # Emit imports
    _emit_module_header(ctx, body)

    # Emit module body (skip imports, already emitted)
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        kind = _str(stmt, "kind")
        if kind in ("ImportFrom", "Import"):
            continue
        _emit_stmt(ctx, stmt)

    # Emit main guard
    if len(main_guard) > 0:
        _emit_blank(ctx)
        _emit(ctx, "// main")
        _emit_body(ctx, main_guard)

    output = "\n".join(ctx.lines).rstrip() + "\n"
    return output
