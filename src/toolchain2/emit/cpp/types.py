"""C++ type mapping from EAST3 resolved types.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations


_TYPE_MAP: dict[str, str] = {
    "int": "int64_t",
    "int8": "int8_t",
    "int16": "int16_t",
    "int32": "int32_t",
    "int64": "int64_t",
    "uint8": "uint8_t",
    "uint16": "uint16_t",
    "uint32": "uint32_t",
    "uint64": "uint64_t",
    "float": "double",
    "float32": "float",
    "float64": "double",
    "bool": "bool",
    "str": "std::string",
    "None": "void",
    "none": "void",
    "bytes": "std::vector<uint8_t>",
    "bytearray": "std::vector<uint8_t>",
}


def cpp_type(resolved_type: str) -> str:
    """Convert an EAST3 resolved_type to a C++ type string."""
    if resolved_type == "" or resolved_type == "unknown":
        return "auto"

    mapped = _TYPE_MAP.get(resolved_type, "")
    if mapped != "":
        return mapped

    # list[T] → std::vector<T>
    if resolved_type.startswith("list[") and resolved_type.endswith("]"):
        inner = resolved_type[5:-1]
        return "std::vector<" + cpp_type(inner) + ">"

    # dict[K, V] → std::unordered_map<K, V>
    if resolved_type.startswith("dict[") and resolved_type.endswith("]"):
        inner = resolved_type[5:-1]
        parts = _split_generic_args(inner)
        if len(parts) == 2:
            return "std::unordered_map<" + cpp_type(parts[0]) + ", " + cpp_type(parts[1]) + ">"

    # set[T] → std::unordered_set<T>
    if resolved_type.startswith("set[") and resolved_type.endswith("]"):
        inner = resolved_type[4:-1]
        return "std::unordered_set<" + cpp_type(inner) + ">"

    # tuple[A, B, ...]
    if resolved_type.startswith("tuple[") and resolved_type.endswith("]"):
        inner = resolved_type[6:-1]
        parts = _split_generic_args(inner)
        if len(parts) > 0:
            return "std::tuple<" + ", ".join(cpp_type(p) for p in parts) + ">"

    # Optional / None union
    if resolved_type.endswith(" | None"):
        inner = resolved_type[:-7]
        return "std::optional<" + cpp_type(inner) + ">"

    # Union → auto (simplified)
    if " | " in resolved_type:
        return "auto"

    # User class → ClassName (by value or shared_ptr depending on context)
    return resolved_type


def cpp_zero_value(resolved_type: str) -> str:
    ct = cpp_type(resolved_type)
    if ct in ("int8_t", "int16_t", "int32_t", "int64_t",
              "uint8_t", "uint16_t", "uint32_t", "uint64_t"):
        return "0"
    if ct in ("float", "double"):
        return "0.0"
    if ct == "bool":
        return "false"
    if ct == "std::string":
        return '""'
    return "{}"


def _split_generic_args(s: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in s:
        if ch == "[" or ch == "<":
            depth += 1
            current.append(ch)
        elif ch == "]" or ch == ">":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail != "":
        parts.append(tail)
    return parts
