from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from toolchain2.emit.scala.emitter import emit_scala_module
from toolchain2.emit.kotlin.emitter import emit_kotlin_module


def _module_doc(module_id: str) -> dict[str, object]:
    return {
        "kind": "Module",
        "east_stage": 3,
        "schema_version": 1,
        "meta": {"module_id": module_id, "dispatch_mode": "native"},
        "body": [],
    }


class JvmBootstrapEmitterTests(unittest.TestCase):
    def test_scala_bootstrap_emitter_imports_and_emits_empty_module(self) -> None:
        out = emit_scala_module(_module_doc("pkg.demo"))
        self.assertIn("object pkg_demo", out)
        self.assertIn("bootstrap scaffold", out)

    def test_kotlin_bootstrap_emitter_imports_and_emits_empty_module(self) -> None:
        out = emit_kotlin_module(_module_doc("pkg.demo"))
        self.assertIn("object pkg_demo", out)
        self.assertIn("bootstrap scaffold", out)

    def test_scala_emits_class_and_method_bootstrap_subset(self) -> None:
        out = emit_scala_module(
            {
                "kind": "Module",
                "east_stage": 3,
                "schema_version": 1,
                "meta": {"module_id": "pkg.demo", "dispatch_mode": "native"},
                "body": [
                    {
                        "kind": "ClassDef",
                        "name": "Holder",
                        "body": [
                            {
                                "kind": "AnnAssign",
                                "target": {"kind": "Name", "id": "msg"},
                                "decl_type": "str",
                                "value": None,
                            },
                            {
                                "kind": "ClosureDef",
                                "name": "__str__",
                                "arg_order": ["self"],
                                "arg_types": {"self": "Holder"},
                                "return_type": "str",
                                "body": [
                                    {
                                        "kind": "Return",
                                        "value": {
                                            "kind": "Attribute",
                                            "value": {"kind": "Name", "id": "self"},
                                            "attr": "msg",
                                        },
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        )
        self.assertIn("class Holder", out)
        self.assertIn("var msg: String = \"\"", out)
        self.assertIn("def __str__(): String", out)
        self.assertIn("return this.msg", out)

    def test_kotlin_emits_import_fixture_subset(self) -> None:
        out = emit_kotlin_module(
            {
                "kind": "Module",
                "east_stage": 3,
                "schema_version": 1,
                "meta": {"module_id": "pkg.demo", "dispatch_mode": "native"},
                "body": [
                    {
                        "kind": "FunctionDef",
                        "name": "probe",
                        "arg_order": [],
                        "arg_types": {},
                        "return_type": "bool",
                        "body": [
                            {
                                "kind": "Assign",
                                "target": {"kind": "Name", "id": "table"},
                                "value": {"kind": "Dict", "keys": [], "values": []},
                            },
                            {
                                "kind": "Return",
                                "value": {
                                    "kind": "BoolOp",
                                    "op": "And",
                                    "values": [
                                        {
                                            "kind": "Compare",
                                            "left": {"kind": "Constant", "value": 1},
                                            "ops": ["LtE"],
                                            "comparators": [{"kind": "Constant", "value": 2}],
                                        },
                                        {
                                            "kind": "IfExp",
                                            "test": {"kind": "Constant", "value": True},
                                            "body": {"kind": "Constant", "value": True},
                                            "orelse": {"kind": "Constant", "value": False},
                                        },
                                    ],
                                },
                            },
                        ],
                    }
                ],
            }
        )
        self.assertIn("var table = linkedMapOf()", out)
        self.assertIn("return (1L <= 2L && (if (true) true else false))", out)


if __name__ == "__main__":
    unittest.main()
