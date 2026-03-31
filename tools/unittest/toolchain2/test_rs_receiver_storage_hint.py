from __future__ import annotations

import unittest

from toolchain2.emit.rs.emitter import emit_rs_module


def _module_doc(body: list[dict[str, object]]) -> dict[str, object]:
    return {
        "kind": "Module",
        "east_stage": 3,
        "schema_version": 1,
        "source_path": "app/main.py",
        "meta": {
            "module_id": "app.main",
            "dispatch_mode": "native",
            "linked_program_v1": {
                "module_id": "app.main",
                "entry_modules": ["app.main"],
                "type_id_resolved_v1": {},
                "type_id_base_map_v1": {},
                "type_info_table_v1": {},
                "resolved_dependencies_v1": [],
                "user_module_dependencies_v1": [],
                "non_escape_summary": {},
                "container_ownership_hints_v1": {},
            },
        },
        "body": body,
    }


class RsReceiverStorageHintTests(unittest.TestCase):
    def test_receiver_storage_hint_forces_borrow_on_property_and_method(self) -> None:
        doc = _module_doc(
            [
                {
                    "kind": "FunctionDef",
                    "name": "prop",
                    "arg_order": ["child"],
                    "arg_types": {"child": "Path"},
                    "return_type": "str",
                    "body": [
                        {
                            "kind": "Return",
                            "value": {
                                "kind": "Attribute",
                                "value": {"kind": "Name", "id": "child", "resolved_type": "Path"},
                                "attr": "name",
                                "resolved_type": "str",
                                "attribute_access_kind": "property_getter",
                                "receiver_storage_hint": "ref",
                            },
                        }
                    ],
                },
                {
                    "kind": "FunctionDef",
                    "name": "meth",
                    "arg_order": ["child"],
                    "arg_types": {"child": "Path"},
                    "return_type": "int64",
                    "body": [
                        {
                            "kind": "Return",
                            "value": {
                                "kind": "Call",
                                "func": {
                                    "kind": "Attribute",
                                    "value": {"kind": "Name", "id": "child", "resolved_type": "Path"},
                                    "attr": "write_text",
                                    "resolved_type": "callable",
                                    "receiver_storage_hint": "ref",
                                },
                                "args": [{"kind": "Constant", "value": "42", "resolved_type": "str"}],
                                "keywords": [],
                                "resolved_type": "int64",
                                "receiver_storage_hint": "ref",
                            },
                        }
                    ],
                },
            ]
        )

        emitted = emit_rs_module(doc)
        self.assertIn("child.borrow().name()", emitted)
        self.assertIn("child.borrow_mut().write_text(", emitted)


if __name__ == "__main__":
    unittest.main()
