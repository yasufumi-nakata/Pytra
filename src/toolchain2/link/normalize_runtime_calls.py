"""Normalize runtime_call values to match emitter expectations.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。

toolchain2 の resolve/compile が設定する runtime_call と、
既存 emitter (toolchain/emit/cpp) が期待する runtime_call にずれがある。
このパスは linked module の BuiltinCall ノードの runtime_call を正規化する。

注: これは暫定互換レイヤ。toolchain2/emit/ が完成すれば不要になる。
"""

from __future__ import annotations

from pytra.std.json import JsonVal


# runtime_call の正規化マップ
# key: toolchain2 が生成する値, value: 旧 emitter が期待する値
_RUNTIME_CALL_MAP: dict[str, str] = {
    # Fallback mappings for cases resolve didn't specialize
    "int": "static_cast",
    "float": "static_cast",
    "str": "py_to_string",
    "bool": "static_cast",
    "len": "py_len",
    # resolve now specializes these, but old C++ emitter needs static_cast
    "py_int_from_str": "static_cast",
    "py_float_from_str": "static_cast",
    "list.index": "py_list_index",
    "pathlib.write_text": "py_write_text",
    "pathlib.read_text": "py_read_text",
}

# str method runtime_calls that should be de-lowered for the old C++ emitter.
# resolve now outputs str.X form (e.g. str.strip, str.join).
# The old C++ emitter's selfhost fallback handles these better as plain Attribute calls.
_STR_METHOD_RUNTIME_CALLS: set[str] = {
    "str.join", "str.strip", "str.lstrip", "str.rstrip",
    "str.startswith", "str.endswith", "str.replace",
    "str.find", "str.rfind", "str.upper", "str.lower",
    "str.split", "str.count", "str.index",
    "str.isdigit", "str.isalpha", "str.isalnum", "str.isspace",
    "str.isupper", "str.islower", "str.title", "str.capitalize",
    "str.zfill", "str.ljust", "str.rjust", "str.center", "str.encode",
    "str.format",
}

# builtin_name ベースのコンストラクタ正規化
_CTOR_MAP: dict[str, str] = {
    "bytearray": "bytearray_ctor",
    "bytes": "bytes_ctor",
    "set": "set_ctor",
}


# BuiltinCalls that should be de-lowered (emitter doesn't have handlers)
_DELOWER_BUILTIN_CALLS: set[str] = {
    "type", "sum", "py_list_index", "list.insert",
}


def normalize_runtime_calls(doc: dict[str, JsonVal]) -> None:
    """Walk the EAST3 doc and normalize runtime_call values in-place."""
    _walk(doc)


# Names that should be lowered to BuiltinCall if they appear as plain Call
_BUILTIN_CALL_NAMES: set[str] = {
    "bytearray", "bytes", "set", "list", "dict",
    "int", "float", "str", "bool",
    "len", "enumerate", "reversed", "range",
    "print", "type", "isinstance", "issubclass",
    "ord", "chr", "abs", "min", "max", "sum",
    "any", "all", "sorted", "zip", "map", "filter",
    "iter", "next", "hash", "id", "repr",
    "round", "divmod", "pow",
}

# Method names that should NOT be lowered to BuiltinCall.
# These are handled by the emitter's selfhost fallback or native C++ method calls.
# Only container mutation methods (append/extend/insert/pop/etc) need BuiltinCall lowering
# because the emitter dispatches them via runtime_call, not C++ method syntax.

# Method names that SHOULD be lowered to BuiltinCall (emitter expects these as BuiltinCall)
_BUILTIN_METHOD_LOWER: dict[str, str] = {
    # list mutation methods — emitter routes via BuiltinCall
    "append": "list.append",
    "extend": "list.extend",
    "insert": "list.insert",
    "remove": "list.remove",
    "pop": "list.pop",
    "clear": "list.clear",
    "sort": "list.sort",
    "reverse": "list.reverse",
    # set mutation
    "add": "set.add",
    "discard": "set.discard",
    # pathlib methods
    "write_text": "pathlib.write_text",
    "read_text": "pathlib.read_text",
}


def _walk(node: JsonVal) -> None:
    """Recursively walk and normalize BuiltinCall nodes."""
    if isinstance(node, dict):
        kind = node.get("kind")
        lk = node.get("lowered_kind")

        if kind == "Call":
            if lk == "BuiltinCall":
                rc = node.get("runtime_call")
                bn = node.get("builtin_name")
                # De-lower str method BuiltinCalls: emitter selfhost fallback
                # handles them better as plain Attribute calls.
                if isinstance(rc, str) and rc in _STR_METHOD_RUNTIME_CALLS:
                    node["lowered_kind"] = ""
                    node["runtime_call"] = ""
                # enumerate/reversed: keep runtime_call for for-stmt detection
                # but remove BuiltinCall lowering since the BuiltinCall handler
                # doesn't know these — the for-stmt handler reads runtime_call.
                elif isinstance(rc, str) and rc in (
                    "py_enumerate_object", "py_reversed_object",
                ):
                    node["lowered_kind"] = ""
                    node["runtime_call"] = "py_enumerate" if "enumerate" in rc else "py_reversed"
                # type/sum/etc: emitter doesn't have BuiltinCall handlers for these.
                # De-lower so they become regular function calls.
                elif isinstance(rc, str) and rc in _DELOWER_BUILTIN_CALLS:
                    node["lowered_kind"] = ""
                elif isinstance(rc, str) and rc in _RUNTIME_CALL_MAP:
                    node["runtime_call"] = _RUNTIME_CALL_MAP[rc]
                elif isinstance(bn, str) and bn in _CTOR_MAP:
                    if isinstance(rc, str) and (rc == bn or rc == ""):
                        node["runtime_call"] = _CTOR_MAP[bn]
            elif lk == "" or lk is None:
                # Not yet lowered: check if it should be
                _try_lower_call(node)

        for v in node.values():
            _walk(v)
    elif isinstance(node, list):
        for item in node:
            _walk(item)


def _try_lower_call(call_node: dict[str, JsonVal]) -> None:
    """Try to lower a plain Call to BuiltinCall if it matches known builtins."""
    func = call_node.get("func")
    if not isinstance(func, dict):
        return

    func_kind = func.get("kind")

    if func_kind == "Name":
        # Direct function call: bytearray(), bytes(), etc.
        func_id = func.get("id")
        if isinstance(func_id, str) and func_id in _BUILTIN_CALL_NAMES:
            call_node["lowered_kind"] = "BuiltinCall"
            call_node["builtin_name"] = func_id
            # Set runtime_call
            if func_id in _CTOR_MAP:
                call_node["runtime_call"] = _CTOR_MAP[func_id]
            elif func_id in _RUNTIME_CALL_MAP:
                call_node["runtime_call"] = _RUNTIME_CALL_MAP[func_id]
            else:
                call_node["runtime_call"] = func_id

    elif func_kind == "Attribute":
        # Method call: x.append(), s.strip(), etc.
        attr = func.get("attr")
        if not isinstance(attr, str):
            return
        if attr in _BUILTIN_METHOD_LOWER:
            call_node["lowered_kind"] = "BuiltinCall"
            call_node["builtin_name"] = attr
            qualified = _BUILTIN_METHOD_LOWER[attr]
            if qualified in _RUNTIME_CALL_MAP:
                call_node["runtime_call"] = _RUNTIME_CALL_MAP[qualified]
            else:
                call_node["runtime_call"] = qualified
