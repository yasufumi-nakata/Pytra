"""toolchain2-compatible C++ header generation for runtime modules."""

from __future__ import annotations

from dataclasses import dataclass
import re

import pytra.std.json as json
from pytra.std.json import JsonVal

from toolchain.emit.cpp.runtime_paths import collect_cpp_dependency_module_ids, cpp_include_for_module
from toolchain.emit.cpp.types import cpp_param_decl, cpp_signature_type, collect_cpp_type_vars, cpp_alias_union_expansion


@dataclass
class CppIncludeDraft:
    path: str

    def to_line(self) -> str:
        return '#include "' + self.path + '"'


def _split_top_level_union(text: str) -> list[str]:
    out: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in text:
        if ch in "[<(":
            depth += 1
        elif ch in "]>)":
            depth -= 1
        elif ch == "|" and depth == 0:
            part = "".join(current).strip()
            if part != "":
                out.append(part)
            current = []
            continue
        current.append(ch)
    tail = "".join(current).strip()
    if tail != "":
        out.append(tail)
    return out


def _recursive_alias_lane_cpp(alias_name: str, lane: str) -> str:
    if lane == "list[" + alias_name + "]":
        return "Object<list<" + alias_name + ">>"
    if lane == "dict[str," + alias_name + "]":
        return "Object<dict<str, " + alias_name + ">>"
    if lane == "set[" + alias_name + "]":
        return "Object<set<" + alias_name + ">>"
    lane_copy = lane + ""
    return cpp_signature_type(lane_copy) + ""


def _emit_recursive_union_alias_decl(lines: list[str], node: dict[str, JsonVal]) -> bool:
    name = _str(node, "name")
    value = cpp_alias_union_expansion(name)
    if value == "":
        value = _str(node, "value")
    if name == "" or value == "":
        return False
    lanes = _split_top_level_union(value)
    if len(lanes) == 0:
        return False
    non_none = [lane for lane in lanes if lane not in ("None", "none")]
    has_none = len(non_none) < len(lanes)
    recursive_lanes = [
        lane for lane in non_none
        if lane in ("list[" + name + "]", "dict[str," + name + "]", "set[" + name + "]")
    ]
    if len(recursive_lanes) == 0:
        return False
    lane_cpp = [_recursive_alias_lane_cpp(name, lane) for lane in non_none]
    variant_type = "::std::variant<" + ", ".join(lane_cpp) + ">"
    base_type = "::std::optional<" + variant_type + ">" if has_none else variant_type

    lines.append("struct " + name + " : " + base_type + " {")
    lines.append("    using base_type = " + base_type + ";")
    lines.append("    using base_type::base_type;")
    lines.append("    using base_type::operator=;")
    if has_none:
        lines.append("    " + name + "() : base_type(::std::nullopt) {}")
    else:
        lines.append("    " + name + "() : base_type() {}")
    for lane in recursive_lanes:
        if lane == "list[" + name + "]":
            list_obj = "Object<list<" + name + ">>"
            lines.append(
                "    " + name + "(const list<" + name + ">& v) : base_type(" + variant_type + "(rc_from_value(v))) {}"
            )
            lines.append(
                "    " + name + "(list<" + name + ">&& v) : base_type(" + variant_type + "(rc_from_value(::std::move(v)))) {}"
            )
            lines.append(
                "    " + name + "(const " + list_obj + "& v) : base_type(" + variant_type + "(v)) {}"
            )
        elif lane == "dict[str," + name + "]":
            dict_obj = "Object<dict<str, " + name + ">>"
            lines.append(
                "    " + name + "(const dict<str, " + name + ">& v) : base_type(" + variant_type + "(rc_from_value(v))) {}"
            )
            lines.append(
                "    " + name + "(dict<str, " + name + ">&& v) : base_type(" + variant_type + "(rc_from_value(::std::move(v)))) {}"
            )
            lines.append(
                "    " + name + "(const " + dict_obj + "& v) : base_type(" + variant_type + "(v)) {}"
            )
        elif lane == "set[" + name + "]":
            set_obj = "Object<set<" + name + ">>"
            lines.append(
                "    " + name + "(const set<" + name + ">& v) : base_type(" + variant_type + "(rc_from_value(v))) {}"
            )
            lines.append(
                "    " + name + "(set<" + name + ">&& v) : base_type(" + variant_type + "(rc_from_value(::std::move(v)))) {}"
            )
            lines.append(
                "    " + name + "(const " + set_obj + "& v) : base_type(" + variant_type + "(v)) {}"
            )
    lines.append("    template <class T, class = decltype(::std::declval<T&>().to_jv())>")
    lines.append("    " + name + "(T v) : base_type(" + variant_type + "(v.to_jv())) {}")
    lines.append("};")
    lines.append(
        "static inline ::std::string py_to_string(const " + name + "& v) { return py_to_string(static_cast<const " + name + "::base_type&>(v)); }"
    )
    lines.append("")
    return True


def build_cpp_header_from_east3(
    module_id: str,
    east_doc: dict[str, JsonVal],
    *,
    rel_header_path: str,
    native_header_include: str = "",
    prefer_native_header: bool = False,
) -> str:
    meta = east_doc.get("meta")
    meta_obj = json.JsonValue(meta).as_obj()
    meta_dict: dict[str, JsonVal] = {}
    if meta_obj is not None:
        meta_dict = meta_obj.raw
    dep_ids = collect_cpp_dependency_module_ids(module_id, meta_dict)
    guard = _header_guard(rel_header_path)
    stmts = _list(east_doc, "body")

    lines: list[str] = [
        "// AUTO-GENERATED by toolchain2/emit/cpp",
        "#ifndef " + guard,
        "#define " + guard,
        "",
        '#include "core/py_runtime.h"',
        '#include <utility>',
    ]
    if _module_needs_functional(stmts):
        lines.append("#include <functional>")

    seen: set[str] = {"core/py_runtime.h"}
    if prefer_native_header and native_header_include != "":
        if native_header_include not in seen:
            lines.append('#include "' + native_header_include + '"')
        lines.extend([
            "",
            "#endif  // " + guard,
            "",
        ])
        return "\n".join(lines)

    for dep_id in dep_ids:
        include_path = cpp_include_for_module(dep_id)
        if include_path == "" or include_path in seen:
            continue
        seen.add(include_path)
        lines.append(CppIncludeDraft(include_path).to_line())
    if native_header_include != "" and native_header_include not in seen:
        lines.append(CppIncludeDraft(native_header_include).to_line())
    lines.append("")

    class_names: list[str] = []
    for stmt in stmts:
        stmt_obj = json.JsonValue(stmt).as_obj()
        if stmt_obj is None or _str(stmt_obj.raw, "kind") != "ClassDef":
            continue
        name = _str(stmt_obj.raw, "name")
        if name != "":
            class_names.append(name)
    if len(class_names) > 0:
        for name in class_names:
            lines.append("struct " + name + ";")
        lines.append("")
    for stmt in stmts:
        _emit_decl(lines, stmt)

    lines.extend([
        "",
        "#endif  // " + guard,
        "",
    ])
    return "\n".join(lines)


def _emit_decl(lines: list[str], stmt: JsonVal) -> None:
    stmt_obj = json.JsonValue(stmt).as_obj()
    if stmt_obj is None:
        return
    stmt_dict = stmt_obj.raw
    kind = _str(stmt_dict, "kind")
    if kind in ("Import", "ImportFrom", "Pass"):
        return
    if kind == "TypeAlias":
        _emit_recursive_union_alias_decl(lines, stmt_dict)
        return
    if kind == "Expr":
        value = stmt_dict.get("value")
        value_obj = json.JsonValue(value).as_obj()
        if value_obj is not None and _str(value_obj.raw, "kind") == "Constant" and _json_str_value(value_obj.raw.get("value")) != "":
            return
    if kind in ("FunctionDef", "ClosureDef"):
        sig = _function_decl(stmt_dict)
        if sig != "":
            lines.append(sig + ";")
        return
    if kind in ("AnnAssign", "Assign"):
        decl = _global_decl(stmt_dict)
        if decl != "":
            lines.append(decl + ";")
        return
    if kind == "ClassDef":
        _emit_class_decl(lines, stmt_dict)


def _function_decl(node: dict[str, JsonVal], *, owner_name: str = "", in_class: bool = False) -> str:
    name = _safe_cpp_ident(_str(node, "name"))
    if name == "":
        return ""
    params = _function_params(node)
    if name == "__init__" and owner_name != "":
        return owner_name + "(" + ", ".join(params) + ")"
    return_type = _return_type(node)
    ret = cpp_signature_type(return_type)
    prefix = ""
    static_prefix = ""
    suffix = ""
    if owner_name != "" and not in_class:
        prefix = owner_name + "::"
    if owner_name != "" and _has_decorator(node, "staticmethod") and in_class:
        static_prefix = "static "
    if owner_name != "" and not _has_decorator(node, "staticmethod") and name != "__init__" and not _function_self_mutates(node):
        suffix = " const"
    signature = static_prefix + ret + " " + prefix + name + "(" + ", ".join(params) + ")" + suffix
    template_prefix = _function_template_prefix(node)
    if template_prefix != "":
        return template_prefix + "\n" + signature
    return signature


def _global_decl(node: dict[str, JsonVal]) -> str:
    target = node.get("target")
    name = _safe_cpp_ident(_target_name(target))
    if name == "":
        return ""
    decl_type = _str(node, "decl_type")
    if decl_type == "":
        decl_type = _str(node, "resolved_type")
    if decl_type == "":
        return ""
    return "extern " + cpp_signature_type(decl_type) + " " + name


def _emit_class_decl(lines: list[str], node: dict[str, JsonVal]) -> None:
    name = _str(node, "name")
    if name == "":
        return
    base_specs: list[str] = []
    base = _str(node, "base")
    if base != "" and base != "object" and not _bool(node, "is_trait"):
        base_specs.append("public " + base)
    trait_names = node.get("trait_names")
    trait_names_arr = json.JsonValue(trait_names).as_arr()
    if trait_names_arr is not None:
        for trait_name in trait_names_arr.raw:
            trait_text = _json_str_value(trait_name)
            if trait_text != "":
                base_specs.append("virtual public " + trait_text)
    header = "struct " + name
    if len(base_specs) > 0:
        header += " : " + ", ".join(base_specs)
    header += " {"
    lines.append(header)
    field_types = _dict(node, "field_types")
    for field_name, field_type in field_types.items():
        field_type_text = _json_str_value(field_type)
        if field_name != "" and field_type_text != "":
            field_type_copy = field_type_text + ""
            lines.append("    " + cpp_signature_type(field_type_copy) + " " + field_name + ";")
    stmts = _list(node, "body")
    for child in stmts:
        child_obj = json.JsonValue(child).as_obj()
        if child_obj is None or _str(child_obj.raw, "kind") not in ("FunctionDef", "ClosureDef"):
            continue
        sig = _function_decl(child_obj.raw, owner_name=name, in_class=True)
        if sig != "":
            lines.append("    " + sig + ";")
    lines.append("};")
    lines.append("")


def _function_params(node: dict[str, JsonVal]) -> list[str]:
    params: list[str] = []
    order = _list(node, "arg_order")
    types = _dict(node, "arg_types")
    defaults = _dict(node, "arg_defaults")
    usage = _dict(node, "arg_usage")
    is_static = _has_decorator(node, "staticmethod")
    for arg in order:
        arg_text = _json_str_value(arg)
        if arg_text == "":
            continue
        if arg_text == "self" and not is_static:
            continue
        arg_type = types.get(arg_text)
        resolved_type = _json_str_value(arg_type)
        if resolved_type == "":
            resolved_type = "object"
        inferred = _infer_callable_param_type(node, arg_text)
        if inferred != "":
            resolved_type = inferred
        usage_text = _json_str_value(usage.get(arg_text))
        text = cpp_param_decl(resolved_type, _safe_cpp_ident(arg_text), is_mutable=usage_text == "reassigned")
        default_node = defaults.get(arg_text)
        default_obj = json.JsonValue(default_node).as_obj()
        if default_obj is not None:
            default_text = _render_default_expr(default_obj.raw)
            if default_text != "":
                text += " = " + default_text
        params.append(text)
    return params


def _function_template_prefix(node: dict[str, JsonVal]) -> str:
    params = _function_template_params(node)
    if len(params) == 0:
        return ""
    return "template <" + ", ".join("class " + name for name in params) + ">"


def _function_template_params(node: dict[str, JsonVal]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    arg_types = _dict(node, "arg_types")
    for arg_type in arg_types.values():
        arg_type_text = _json_str_value(arg_type)
        if arg_type_text != "":
            for type_var in collect_cpp_type_vars(arg_type_text):
                if type_var not in seen:
                    seen.add(type_var)
                    out.append(type_var)
    for type_var in collect_cpp_type_vars(_return_type(node)):
        if type_var not in seen:
            seen.add(type_var)
            out.append(type_var)
    return out


def _function_self_mutates(node: dict[str, JsonVal]) -> bool:
    if _bool(node, "mutates_self"):
        return True
    arg_usage = _dict(node, "arg_usage")
    if _json_str_value(arg_usage.get("self")) == "reassigned":
        return True
    return _node_mutates_self_fields(node.get("body"))


def _node_mutates_self_fields(node: JsonVal) -> bool:
    node_obj = json.JsonValue(node).as_obj()
    if node_obj is not None:
        node_dict = node_obj.raw
        kind = _str(node_dict, "kind")
        if kind in ("Assign", "AugAssign", "AnnAssign"):
            target = node_dict.get("target")
            targets: list[JsonVal] = []
            if target is not None:
                targets.append(target)
            extra_targets_arr = json.JsonValue(node_dict.get("targets")).as_arr()
            if extra_targets_arr is not None:
                targets.extend(extra_targets_arr.raw)
            for candidate in targets:
                candidate_obj = json.JsonValue(candidate).as_obj()
                if candidate_obj is None or _str(candidate_obj.raw, "kind") != "Attribute":
                    continue
                owner_obj = json.JsonValue(candidate_obj.raw.get("value")).as_obj()
                if owner_obj is not None and _str(owner_obj.raw, "kind") == "Name" and _str(owner_obj.raw, "id") == "self":
                    return True
        if kind == "Call":
            meta_obj = json.JsonValue(node_dict.get("meta")).as_obj()
            if meta_obj is not None and _bool(meta_obj.raw, "mutates_receiver"):
                return True
            func_obj = json.JsonValue(node_dict.get("func")).as_obj()
            if func_obj is not None and _str(func_obj.raw, "kind") == "Attribute":
                owner_obj = json.JsonValue(func_obj.raw.get("value")).as_obj()
                if owner_obj is not None and _str(owner_obj.raw, "kind") == "Name" and _str(owner_obj.raw, "id") == "self":
                    return True
                if owner_obj is not None and _str(owner_obj.raw, "kind") == "Attribute":
                    base_obj = json.JsonValue(owner_obj.raw.get("value")).as_obj()
                    if base_obj is not None and _str(base_obj.raw, "kind") == "Name" and _str(base_obj.raw, "id") == "self":
                        call_owner_obj = json.JsonValue(node_dict.get("runtime_owner")).as_obj()
                        if call_owner_obj is not None and _str(call_owner_obj.raw, "borrow_kind") == "mutable_ref":
                            return True
                        runtime_call = _str(node_dict, "runtime_call")
                        if runtime_call in {
                            "list.append",
                            "list.extend",
                            "list.insert",
                            "list.pop",
                            "list.clear",
                            "list.reverse",
                            "list.sort",
                            "dict.pop",
                            "dict.setdefault",
                            "dict.update",
                            "dict.clear",
                            "set.add",
                            "set.discard",
                            "set.remove",
                            "set.clear",
                            "bytearray.append",
                            "bytearray.extend",
                            "bytearray.pop",
                            "bytearray.clear",
                        }:
                            return True
        for value in node_dict.values():
            if _node_mutates_self_fields(value):
                return True
        return False
    node_arr = json.JsonValue(node).as_arr()
    if node_arr is not None:
        for item in node_arr.raw:
            if _node_mutates_self_fields(item):
                return True
    return False


def _render_default_expr(node: dict[str, JsonVal]) -> str:
    kind = _str(node, "kind")
    if kind == "Constant":
        value = node.get("value")
        if value is None:
            return "::std::nullopt"
        bool_value = json.JsonValue(value).as_bool()
        if bool_value is not None:
            return "true" if bool_value else "false"
        int_value = json.JsonValue(value).as_int()
        if int_value is not None:
            return str(int_value)
        float_value = json.JsonValue(value).as_float()
        if float_value is not None:
            return str(float_value)
        str_raw = json.JsonValue(value).as_str()
        if str_raw is not None:
            str_value = str_raw
            return _cpp_string(str_value)
        return ""
    if kind == "Name":
        name = _str(node, "id")
        if name == "None":
            return "::std::nullopt"
        if name == "True":
            return "true"
        if name == "False":
            return "false"
        return name
    if kind == "List":
        resolved_type = _str(node, "resolved_type")
        if resolved_type == "":
            resolved_type = "list[object]"
        items = _list(node, "elements")
        parts: list[str] = []
        for item in items:
            item_obj = json.JsonValue(item).as_obj()
            if item_obj is not None:
                parts.append(_render_default_expr(item_obj.raw))
        return cpp_signature_type(resolved_type) + "{" + ", ".join(parts) + "}"
    if kind == "Dict":
        resolved_type = _str(node, "resolved_type")
        if resolved_type == "":
            resolved_type = "dict[str,object]"
        entries = _list(node, "entries")
        parts: list[str] = []
        for entry in entries:
            entry_obj = json.JsonValue(entry).as_obj()
            if entry_obj is not None:
                parts.append("{" + _render_default_expr_value(entry_obj.raw.get("key")) + ", " + _render_default_expr_value(entry_obj.raw.get("value")) + "}")
        return cpp_signature_type(resolved_type) + "{" + ", ".join(parts) + "}"
    return ""


def _cpp_string(text: str) -> str:
    out: list[str] = ['"']
    for ch in text:
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
        else:
            out.append(ch)
    out.append('"')
    return "str(" + "".join(out) + ")"


def _target_name(target: JsonVal) -> str:
    target_text = _json_str_value(target)
    if target_text != "":
        return target_text
    target_obj = json.JsonValue(target).as_obj()
    if target_obj is not None:
        return _str(target_obj.raw, "id")
    return ""


_CPP_RESERVED_WORDS: set[str] = {
    "alignas", "alignof", "and", "and_eq", "asm", "auto", "bitand", "bitor",
    "bool", "break", "case", "catch", "char", "class", "compl", "concept",
    "const", "consteval", "constexpr", "constinit", "const_cast", "continue",
    "co_await", "co_return", "co_yield", "decltype", "default", "delete", "do",
    "double", "dynamic_cast", "else", "enum", "explicit", "export", "extern",
    "false", "float", "for", "friend", "goto", "if", "inline", "int", "long",
    "mutable", "namespace", "new", "noexcept", "not", "not_eq", "nullptr",
    "operator", "or", "or_eq", "private", "protected", "public", "register",
    "reinterpret_cast", "requires", "return", "short", "signed", "sizeof",
    "static", "static_assert", "static_cast", "struct", "switch", "template",
    "this", "throw", "true", "try", "typedef", "typeid", "typename", "union",
    "unsigned", "using", "virtual", "void", "volatile", "wchar_t", "while",
    "xor", "xor_eq",
}


def _safe_cpp_ident(name: str) -> str:
    if name == "":
        return ""
    safe = re.sub(r"[^0-9A-Za-z_]", "_", name)
    if safe != "" and safe[0].isdigit():
        safe = "_" + safe
    if safe in _CPP_RESERVED_WORDS:
        safe += "_"
    return safe


def _module_needs_functional(stmts: list[JsonVal]) -> bool:
    for stmt in stmts:
        stmt_obj = json.JsonValue(stmt).as_obj()
        if stmt_obj is None:
            continue
        if _node_uses_callable_types(stmt_obj.raw):
            return True
    return False


def _node_uses_callable_types(node: dict[str, JsonVal]) -> bool:
    if _type_uses_callable(_return_type(node)):
        return True
    arg_types = _dict(node, "arg_types")
    for value in arg_types.values():
        value_text = _json_str_value(value)
        if value_text != "" and _type_uses_callable(value_text):
            return True
    body = _list(node, "body")
    for stmt in body:
        stmt_obj = json.JsonValue(stmt).as_obj()
        if stmt_obj is not None:
            if _node_uses_callable_types(stmt_obj.raw):
                return True
    field_types = _dict(node, "field_types")
    for value in field_types.values():
        value_text = _json_str_value(value)
        if value_text != "" and _type_uses_callable(value_text):
            return True
    return False


def _type_uses_callable(resolved_type: str) -> bool:
    return (
        resolved_type == "callable"
        or resolved_type == "Callable"
        or resolved_type.startswith("callable[")
        or resolved_type.startswith("Callable[")
    )


def _infer_callable_param_type(node: dict[str, JsonVal], param_name: str) -> str:
    declared = ""
    arg_types = _dict(node, "arg_types")
    declared = _json_str_value(arg_types.get(param_name))
    if not _type_uses_callable(declared):
        return ""
    inferred_arg = ""
    inferred_ret = ""

    def visit(cur: JsonVal, parent: JsonVal, grandparent: JsonVal) -> None:
        nonlocal inferred_arg, inferred_ret
        cur_obj = json.JsonValue(cur).as_obj()
        if cur_obj is not None:
            cur_dict = cur_obj.raw
            if _str(cur_dict, "kind") == "Call":
                func_obj = json.JsonValue(cur_dict.get("func")).as_obj()
                if func_obj is not None and _str(func_obj.raw, "kind") == "Name" and _str(func_obj.raw, "id") == param_name:
                    args = _list(cur_dict, "args")
                    if len(args) == 1:
                        arg_obj = json.JsonValue(args[0]).as_obj()
                        arg_type = _str(arg_obj.raw, "resolved_type") if arg_obj is not None else ""
                        if arg_type not in ("", "unknown", "object", "Any", "Callable", "callable"):
                            inferred_arg = arg_type
                    ret_type = _infer_callable_return_from_parent(cur_dict, parent, grandparent, node)
                    if ret_type not in ("", "unknown", "object", "Any", "Callable", "callable"):
                        inferred_ret = ret_type
            for child in cur_dict.values():
                visit(child, cur_dict, parent)
            return
        cur_arr = json.JsonValue(cur).as_arr()
        if cur_arr is not None:
            for child in cur_arr.raw:
                visit(child, parent, grandparent)

    body = _list(node, "body")
    for stmt in body:
        visit(stmt, node, None)
    if inferred_arg != "" and inferred_ret != "":
        return "callable[[" + inferred_arg + "]," + inferred_ret + "]"
    return ""


def _infer_callable_return_from_parent(
    call_node: dict[str, JsonVal],
    parent: JsonVal,
    grandparent: JsonVal,
    func_node: dict[str, JsonVal],
) -> str:
    parent_obj = json.JsonValue(parent).as_obj()
    if parent_obj is not None:
        parent_dict = parent_obj.raw
        parent_kind = _str(parent_dict, "kind")
        if parent_kind == "Return":
            return _return_type(func_node)
        if parent_kind == "Unbox":
            resolved = _str(parent_dict, "resolved_type")
            if resolved != "":
                return resolved
        if parent_kind == "Call":
            runtime_call = _str(parent_dict, "runtime_call")
            if runtime_call == "list.append":
                owner_obj = json.JsonValue(parent_dict.get("runtime_owner")).as_obj()
                if owner_obj is not None:
                    owner_type = _str(owner_obj.raw, "resolved_type")
                    if owner_type.startswith("list[") and owner_type.endswith("]"):
                        return owner_type[5:-1]
            func_obj = json.JsonValue(parent_dict.get("func")).as_obj()
            call_func_obj = json.JsonValue(call_node.get("func")).as_obj()
            call_func_name = _str(call_func_obj.raw, "id") if call_func_obj is not None else ""
            if func_obj is not None and _str(func_obj.raw, "kind") == "Name" and _str(func_obj.raw, "id") == call_func_name:
                grandparent_obj = json.JsonValue(grandparent).as_obj()
                if grandparent_obj is not None and _str(grandparent_obj.raw, "kind") == "Return":
                    return _return_type(func_node)
                if grandparent_obj is not None and _str(grandparent_obj.raw, "kind") == "Unbox":
                    resolved = _str(grandparent_obj.raw, "resolved_type")
                    if resolved != "":
                        return resolved
        if parent_kind in ("Assign", "AnnAssign"):
            return _str(parent_dict, "decl_type")
    return ""


def _return_type(node: dict[str, JsonVal]) -> str:
    return_type = _str(node, "return_type")
    if return_type == "":
        return_type = _str(node, "returns")
    if return_type == "":
        return_type = "None"
    return return_type


def _has_decorator(node: dict[str, JsonVal], name: str) -> bool:
    decorators = node.get("decorators")
    decorators_arr = json.JsonValue(decorators).as_arr()
    if decorators_arr is None:
        return False
    for decorator in decorators_arr.raw:
        if _json_str_value(decorator) == name:
            return True
    return False


def _header_guard(rel_header_path: str) -> str:
    parts: list[str] = []
    for ch in rel_header_path:
        if ch.isalnum():
            parts.append(ch.upper())
        else:
            parts.append("_")
    return "PYTRA_GEN_" + "".join(parts)


def _str(node: dict[str, JsonVal], key: str) -> str:
    value = node.get(key)
    raw = json.JsonValue(value).as_str()
    if raw is not None:
        return raw
    return ""


def _bool(node: dict[str, JsonVal], key: str) -> bool:
    value = node.get(key)
    raw = json.JsonValue(value).as_bool()
    if raw is not None:
        return raw
    return False


def _json_str_value(value: JsonVal) -> str:
    raw = json.JsonValue(value).as_str()
    if raw is not None:
        return raw
    return ""


def _list(node: dict[str, JsonVal], key: str) -> list[JsonVal]:
    value = json.JsonValue(node.get(key)).as_arr()
    if value is not None:
        return value.raw
    return []


def _dict(node: dict[str, JsonVal], key: str) -> dict[str, JsonVal]:
    value = json.JsonValue(node.get(key)).as_obj()
    if value is not None:
        return value.raw
    return {}


def _render_default_expr_value(node: JsonVal) -> str:
    node_obj = json.JsonValue(node).as_obj()
    if node_obj is not None:
        return _render_default_expr(node_obj.raw)
    return ""
