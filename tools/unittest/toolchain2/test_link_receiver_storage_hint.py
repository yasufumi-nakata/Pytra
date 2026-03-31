from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from toolchain2.link.linker import link_modules


def _module_doc(
    module_id: str,
    *,
    source_path: str = "",
    body: list[dict[str, object]] | None = None,
    meta_extra: dict[str, object] | None = None,
) -> dict[str, object]:
    meta: dict[str, object] = {
        "module_id": module_id,
        "dispatch_mode": "native",
    }
    if meta_extra:
        meta.update(meta_extra)
    return {
        "kind": "Module",
        "east_stage": 3,
        "schema_version": 1,
        "source_path": source_path or module_id.replace(".", "/") + ".py",
        "meta": meta,
        "body": body if body is not None else [],
    }


def _name(name: str, resolved_type: str = "unknown") -> dict[str, object]:
    return {"kind": "Name", "id": name, "resolved_type": resolved_type}


def _attribute(
    value: dict[str, object],
    attr: str,
    *,
    resolved_type: str,
    attribute_access_kind: str = "field_access",
) -> dict[str, object]:
    return {
        "kind": "Attribute",
        "value": value,
        "attr": attr,
        "resolved_type": resolved_type,
        "attribute_access_kind": attribute_access_kind,
    }


def _expr_stmt(value: dict[str, object]) -> dict[str, object]:
    return {"kind": "Expr", "value": value}


class LinkReceiverStorageHintTests(unittest.TestCase):
    def test_linker_attaches_receiver_storage_hint_to_attribute_and_call(self) -> None:
        runtime_doc = _module_doc(
            "app.pathlib_helper",
            body=[
                {
                    "kind": "ClassDef",
                    "name": "Path",
                    "class_storage_hint": "ref",
                    "body": [
                        {
                            "kind": "ClosureDef",
                            "name": "write_text",
                            "arg_order": ["self", "text"],
                            "arg_types": {"self": "Path", "text": "str"},
                            "return_type": "int64",
                            "body": [],
                        }
                    ],
                }
            ],
        )
        entry_doc = _module_doc(
            "app.main",
            body=[
                _expr_stmt(
                    {
                        "kind": "Call",
                        "func": _name("Path", "callable"),
                        "args": [{"kind": "Constant", "value": "work", "resolved_type": "str"}],
                        "keywords": [],
                        "resolved_type": "Path",
                    }
                ),
                _expr_stmt(
                    _attribute(
                        _name("child", "Path"),
                        "parent",
                        resolved_type="Path",
                        attribute_access_kind="property_getter",
                    )
                ),
                _expr_stmt(
                    {
                        "kind": "Call",
                        "func": _attribute(
                            _name("child", "Path"),
                            "write_text",
                            resolved_type="callable",
                        ),
                        "args": [{"kind": "Constant", "value": "42", "resolved_type": "str"}],
                        "keywords": [],
                        "resolved_type": "int64",
                    }
                ),
            ],
            meta_extra={
                "import_symbols": {
                    "Path": {"module": "app.pathlib_helper", "name": "Path"},
                },
                "import_bindings": [
                    {
                        "module_id": "app.pathlib_helper",
                        "export_name": "Path",
                        "local_name": "Path",
                        "binding_kind": "symbol",
                    }
                ],
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            entry_path = tmpdir / "app.main.east3.json"
            runtime_path = tmpdir / "pytra.std.pathlib.east3.json"
            entry_path.write_text(json.dumps(entry_doc), encoding="utf-8")
            runtime_path.write_text(json.dumps(runtime_doc), encoding="utf-8")
            result = link_modules([str(entry_path), str(runtime_path)], target="rs", dispatch_mode="native")

        linked_entry = next(m.east_doc for m in result.linked_modules if m.module_id == "app.main")
        body = linked_entry.get("body", [])
        assert isinstance(body, list)
        ctor_expr = body[0]
        attr_expr = body[1]
        call_expr = body[2]
        assert isinstance(ctor_expr, dict) and isinstance(attr_expr, dict) and isinstance(call_expr, dict)
        ctor_node = ctor_expr.get("value")
        attr_node = attr_expr.get("value")
        call_node = call_expr.get("value")
        assert isinstance(ctor_node, dict) and isinstance(attr_node, dict) and isinstance(call_node, dict)
        self.assertEqual(ctor_node.get("resolved_storage_hint"), "ref")
        self.assertEqual(attr_node.get("receiver_storage_hint"), "ref")
        self.assertEqual(call_node.get("receiver_storage_hint"), "ref")
        method_sig = call_node.get("method_signature_v1")
        self.assertIsInstance(method_sig, dict)
        self.assertEqual(method_sig.get("name"), "write_text")


if __name__ == "__main__":
    unittest.main()
