"""Go type mapping from EAST3 resolved types.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations


# EAST3 resolved_type → Go type
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
    "str": "string",
    "None": "",
    "none": "",
    "bytes": "[]byte",
    "bytearray": "[]byte",
    "object": "any",
    "Obj": "any",
    "Any": "any",
}


def go_type(resolved_type: str) -> str:
    """Convert an EAST3 resolved_type to a Go type string."""
    if resolved_type == "" or resolved_type == "unknown":
        return "any"

    # Direct mapping
    mapped = _TYPE_MAP.get(resolved_type, "")
    if mapped != "":
        return mapped

    # list[T] → []T
    if resolved_type.startswith("list[") and resolved_type.endswith("]"):
        inner = resolved_type[5:-1]
        return "[]" + go_type(inner)

    # dict[K, V] → map[K]V
    if resolved_type.startswith("dict[") and resolved_type.endswith("]"):
        inner = resolved_type[5:-1]
        parts = _split_generic_args(inner)
        if len(parts) == 2:
            return "map[" + go_type(parts[0]) + "]" + go_type(parts[1])

    # set[T] → map[T]struct{}
    if resolved_type.startswith("set[") and resolved_type.endswith("]"):
        inner = resolved_type[4:-1]
        return "map[" + go_type(inner) + "]struct{}"

    # tuple[A, B, ...] — Go doesn't have tuples, use struct or interface{}
    if resolved_type.startswith("tuple[") and resolved_type.endswith("]"):
        return "interface{}"

    # Optional[T] / T | None → *T (pointer for nilability)
    if resolved_type.endswith(" | None"):
        inner = resolved_type[:-7]
        gt = go_type(inner)
        if gt.startswith("*") or gt == "interface{}":
            return gt
        return "*" + gt

    # Union type (A | B) → interface{}
    if " | " in resolved_type:
        return "interface{}"

    # User class → *ClassName (pointer for reference semantics)
    return "*" + _safe_go_ident(resolved_type)


def go_zero_value(resolved_type: str) -> str:
    """Return the Go zero value for a type."""
    gt = go_type(resolved_type)
    if gt in ("int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"):
        return "0"
    if gt in ("float32", "float64"):
        return "0.0"
    if gt == "bool":
        return "false"
    if gt == "string":
        return "\"\""
    return "nil"


def _safe_go_ident(name: str) -> str:
    """Make a string safe as a Go identifier."""
    _GO_KEYWORDS = {
        "break", "case", "chan", "const", "continue", "default", "defer",
        "else", "fallthrough", "for", "func", "go", "goto", "if", "import",
        "interface", "map", "package", "range", "return", "select", "struct",
        "switch", "type", "var",
    }
    chars: list[str] = []
    for ch in name:
        if ch.isalnum() or ch == "_":
            chars.append(ch)
        else:
            chars.append("_")
    out = "".join(chars)
    if out == "":
        return "_unnamed"
    if out[0].isdigit():
        out = "_" + out
    if out in _GO_KEYWORDS:
        out = out + "_"
    return out


def _split_generic_args(s: str) -> list[str]:
    """Split comma-separated generic type args respecting brackets."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in s:
        if ch == "[":
            depth += 1
            current.append(ch)
        elif ch == "]":
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
