def pick_optional(flag: bool, name: str) -> str | None:
    out = name if flag else None
    return out


def pick_optional_reverse(flag: bool, name: str) -> str | None:
    out = None if flag else name
    return out


def pick_union(flag: bool):
    out = 1 if flag else "x"
    return out
