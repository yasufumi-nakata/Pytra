"""C++ type mapping from EAST3 resolved types.

toolchain2 C++ backend は `src/runtime/cpp/core/*` の公開 alias (`str`,
`list[T]`, `dict[K,V]`, `float64`, `object` など) を正本として使う。
"""

from __future__ import annotations

import re


_TYPE_MAP: dict[str, str] = {
    "int": "int64",
    "int8": "int8",
    "int16": "int16",
    "int32": "int32",
    "int64": "int64",
    "uint8": "uint8",
    "uint16": "uint16",
    "uint32": "uint32",
    "uint64": "uint64",
    "float": "float64",
    "float32": "float32",
    "float64": "float64",
    "bool": "bool",
    "str": "str",
    "PyFile": "pytra::runtime::cpp::base::PyFile",
    "None": "void",
    "none": "void",
    "bytes": "bytes",
    "bytearray": "bytearray",
    "Any": "object",
    "Obj": "object",
    "object": "object",
}


def is_container_resolved_type(resolved_type: str) -> bool:
    return (
        resolved_type.startswith("list[")
        or resolved_type.startswith("dict[")
        or resolved_type.startswith("set[")
    )


def cpp_container_value_type(resolved_type: str) -> str:
    if resolved_type.startswith("list[") and resolved_type.endswith("]"):
        inner = resolved_type[5:-1]
        return "list<" + cpp_signature_type(inner) + ">"
    if resolved_type.startswith("dict[") and resolved_type.endswith("]"):
        inner = resolved_type[5:-1]
        parts = _split_generic_args(inner)
        if len(parts) == 2:
            return "dict<" + cpp_signature_type(parts[0]) + ", " + cpp_signature_type(parts[1]) + ">"
    if resolved_type.startswith("set[") and resolved_type.endswith("]"):
        inner = resolved_type[4:-1]
        return "set<" + cpp_signature_type(inner) + ">"
    return ""


def cpp_type(resolved_type: str, *, prefer_value_container: bool = False) -> str:
    """Convert an EAST3 resolved_type to a C++ type string."""
    if resolved_type == "" or resolved_type == "unknown":
        return "auto"

    mapped = _TYPE_MAP.get(resolved_type, "")
    if mapped != "":
        return mapped

    # list[T] / dict[K, V] / set[T]
    container_value_type = cpp_container_value_type(resolved_type)
    if container_value_type != "":
        if prefer_value_container:
            return container_value_type
        return "Object<" + container_value_type + ">"

    # tuple[A, B, ...]
    if resolved_type.startswith("tuple[") and resolved_type.endswith("]"):
        inner = resolved_type[6:-1]
        parts = _split_generic_args(inner)
        if len(parts) > 0:
            return "::std::tuple<" + ", ".join(cpp_type(p) for p in parts) + ">"

    optional_inner = _top_level_optional_inner(resolved_type)
    if optional_inner != "":
        return "::std::optional<" + cpp_signature_type(optional_inner) + ">"

    # General union → object (variant 導入までは fail-closed)
    if _is_top_level_union(resolved_type):
        return "object"

    # User class → ClassName (by value or shared_ptr depending on context)
    return resolved_type


def cpp_signature_type(resolved_type: str, *, prefer_value_container: bool = False) -> str:
    """Type text for declarations/signatures.

    `unknown` / general union は `auto` にせず fail-closed で `object` に倒す。
    """
    if resolved_type == "" or resolved_type == "unknown":
        return "object"
    if resolved_type in ("Any", "Obj", "object"):
        return "object"
    optional_inner = _top_level_optional_inner(resolved_type)
    if optional_inner != "":
        return "::std::optional<" + cpp_signature_type(
            optional_inner,
            prefer_value_container=prefer_value_container,
        ) + ">"
    if _is_top_level_union(resolved_type):
        return "object"
    return cpp_type(resolved_type, prefer_value_container=prefer_value_container)


def cpp_param_decl(resolved_type: str, name: str, *, mutable: bool = False) -> str:
    """Render a function parameter declaration."""
    ct = cpp_signature_type(resolved_type)
    if _is_small_value_type(ct):
        return ct + " " + name
    if mutable:
        return ct + "& " + name
    return "const " + ct + "& " + name


def cpp_zero_value(resolved_type: str, *, prefer_value_container: bool = False) -> str:
    if is_container_resolved_type(resolved_type):
        container_value_type = cpp_container_value_type(resolved_type)
        if prefer_value_container:
            return container_value_type + "{}"
        if resolved_type.startswith("list[") and resolved_type.endswith("]"):
            inner = resolved_type[5:-1]
            return "rc_list_new<" + cpp_signature_type(inner) + ">()"
        if resolved_type.startswith("dict[") and resolved_type.endswith("]"):
            inner = resolved_type[5:-1]
            parts = _split_generic_args(inner)
            if len(parts) == 2:
                return (
                    "rc_dict_new<"
                    + cpp_signature_type(parts[0])
                    + ", "
                    + cpp_signature_type(parts[1])
                    + ">()"
                )
        if resolved_type.startswith("set[") and resolved_type.endswith("]"):
            inner = resolved_type[4:-1]
            return "rc_set_new<" + cpp_signature_type(inner) + ">()"

    ct = cpp_signature_type(resolved_type, prefer_value_container=prefer_value_container)
    if ct == "void":
        return ""
    if ct == "object":
        return "object()"
    if ct == "auto":
        return "{}"
    return ct + "{}"


def _is_small_value_type(cpp_text: str) -> bool:
    return cpp_text in {
        "bool",
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "float32",
        "float64",
    }


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


def _split_top_level_union(resolved_type: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    i = 0
    while i < len(resolved_type):
        ch = resolved_type[i]
        if ch in "[<(":
            depth += 1
            current.append(ch)
            i += 1
            continue
        if ch in "]>)":
            depth -= 1
            current.append(ch)
            i += 1
            continue
        if ch == "|" and depth == 0:
            part = "".join(current).strip()
            if part != "":
                parts.append(part)
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail != "":
        parts.append(tail)
    return parts


def _is_top_level_union(resolved_type: str) -> bool:
    return len(_split_top_level_union(resolved_type)) > 1


def _top_level_optional_inner(resolved_type: str) -> str:
    parts = _split_top_level_union(resolved_type)
    if len(parts) != 2:
        return ""
    if parts[0] in ("None", "none"):
        return parts[1]
    if parts[1] in ("None", "none"):
        return parts[0]
    return ""


_TYPE_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def collect_cpp_type_vars(resolved_type: str) -> list[str]:
    """Collect generic type-variable names that should become C++ templates."""
    if resolved_type == "":
        return []
    out: list[str] = []
    seen: set[str] = set()
    for token in _TYPE_TOKEN_RE.findall(resolved_type):
        if token in _TYPE_MAP:
            continue
        if token in {
            "list",
            "dict",
            "set",
            "tuple",
            "Callable",
            "Iterator",
            "Iterable",
            "Optional",
            "None",
            "none",
            "object",
            "Any",
            "Obj",
            "unknown",
            "callable",
        }:
            continue
        if token.upper() != token:
            continue
        if token not in seen:
            seen.add(token)
            out.append(token)
    return out
