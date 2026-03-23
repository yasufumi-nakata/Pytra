"""EAST3 yields_dynamic annotation pass.

Marks expression nodes whose *Python-level resolved_type* is known but
whose *target-language runtime return type* is dynamically typed (``any``).

Emitters for statically typed languages (Go, Zig, etc.) use this flag
to decide whether an explicit type cast is required, instead of
pattern-matching on rendered output strings.

Nodes annotated with ``yields_dynamic: true``:

* ``IfExp`` – ternary expression returns ``any`` at runtime because the
  two branches may have different concrete types.
* ``Call`` to ``min`` / ``max`` built-ins – variadic, may mix int/float.
* ``Call`` to ``dict.get(key, default)`` – dict value type is erased at
  runtime in Go's ``map[any]any``.
"""

from __future__ import annotations

from typing import Any


def _mark_yields_dynamic(node: Any) -> None:
    """Recursively walk *node* and set ``yields_dynamic: true``."""
    if isinstance(node, list):
        i = 0
        while i < len(node):
            _mark_yields_dynamic(node[i])
            i += 1
        return
    if not isinstance(node, dict):
        return
    nd: dict[str, Any] = node
    kind = nd.get("kind", "")

    if kind == "IfExp":
        nd["yields_dynamic"] = True

    if kind == "Call":
        func = nd.get("func")
        if isinstance(func, dict):
            func_kind = func.get("kind", "")
            # min(...) / max(...) built-in calls
            if func_kind == "Name":
                callee = func.get("id", "")
                if callee in ("min", "max"):
                    nd["yields_dynamic"] = True
            # dict.get(key, default)
            if func_kind == "Attribute":
                attr = func.get("attr", "")
                if attr == "get":
                    owner = func.get("value")
                    if isinstance(owner, dict):
                        owner_type = owner.get("resolved_type", "")
                        if isinstance(owner_type, str) and owner_type.startswith("dict["):
                            nd["yields_dynamic"] = True

    # Recurse into all child nodes
    for v in nd.values():
        if isinstance(v, dict):
            _mark_yields_dynamic(v)
        elif isinstance(v, list):
            _mark_yields_dynamic(v)


def apply_yields_dynamic(east_doc: dict[str, Any]) -> None:
    """Entry point: annotate *east_doc* in place."""
    _mark_yields_dynamic(east_doc)
