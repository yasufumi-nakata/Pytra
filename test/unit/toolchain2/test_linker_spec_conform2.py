from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from toolchain2.link.linker import LinkedModule, link_modules
from toolchain2.link.expand_defaults import expand_cross_module_defaults
from toolchain2.link.manifest_loader import load_linked_output
from toolchain2.link.runtime_discovery import discover_runtime_modules
from toolchain2.link.type_id import build_type_id_table


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
        "source_path": source_path,
        "meta": meta,
        "body": body if body is not None else [],
    }


def _class_def(
    name: str,
    *,
    base: str | None = None,
    bases: list[str] | None = None,
) -> dict[str, object]:
    node: dict[str, object] = {
        "kind": "ClassDef",
        "name": name,
        "body": [],
    }
    if bases is not None:
        node["bases"] = bases
    else:
        node["base"] = base
    return node


def _linked_module(module_id: str, body: list[dict[str, object]]) -> LinkedModule:
    return LinkedModule(
        module_id=module_id,
        input_path=module_id.replace(".", "/") + ".east3.json",
        source_path=module_id.replace(".", "/") + ".py",
        is_entry=True,
        east_doc=_module_doc(module_id, body=body),
        module_kind="user",
    )


class Toolchain2LinkerSpecConform2Tests(unittest.TestCase):
    def test_type_id_builder_accepts_single_base_from_bases_array(self) -> None:
        modules = [
            _linked_module(
                "app.main",
                [
                    _class_def("Base"),
                    _class_def("Child", bases=["Base"]),
                ],
            )
        ]

        type_id_table, type_id_base_map, type_info_table = build_type_id_table(modules)

        self.assertIn("app.main.Base", type_id_table)
        self.assertIn("app.main.Child", type_id_table)
        self.assertEqual(type_id_base_map["app.main.Child"], type_id_table["app.main.Base"])
        self.assertEqual(type_info_table["app.main.Base"]["id"], type_id_table["app.main.Base"])

    def test_type_id_builder_rejects_multiple_inheritance(self) -> None:
        modules = [
            _linked_module(
                "app.main",
                [
                    _class_def("A"),
                    _class_def("B"),
                    _class_def("C", bases=["A", "B"]),
                ],
            )
        ]

        with self.assertRaisesRegex(RuntimeError, "multiple inheritance is not supported"):
            build_type_id_table(modules)

    def test_type_id_builder_rejects_undefined_base(self) -> None:
        modules = [
            _linked_module(
                "app.main",
                [
                    _class_def("Child", bases=["Missing"]),
                ],
            )
        ]

        with self.assertRaisesRegex(RuntimeError, "undefined base class"):
            build_type_id_table(modules)

    def test_type_id_builder_rejects_inheritance_cycle(self) -> None:
        modules = [
            _linked_module(
                "app.main",
                [
                    _class_def("A", bases=["B"]),
                    _class_def("B", bases=["A"]),
                ],
            )
        ]

        with self.assertRaisesRegex(RuntimeError, "inheritance cycle"):
            build_type_id_table(modules)

    def test_runtime_discovery_rejects_missing_explicit_runtime_module(self) -> None:
        module_map = {
            "/tmp/app.main.east3.json": _module_doc(
                "app.main",
                meta_extra={"import_bindings": [{"module_id": "pytra.std.missing"}]},
            )
        }

        with patch("toolchain2.link.runtime_discovery.resolve_runtime_east_path", return_value=""):
            with self.assertRaisesRegex(RuntimeError, "runtime EAST module not found"):
                discover_runtime_modules(module_map)

    def test_runtime_discovery_rejects_invalid_runtime_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_runtime = Path(tmp) / "bad.east"
            bad_runtime.write_text("{bad json", encoding="utf-8")
            module_map = {
                "/tmp/app.main.east3.json": _module_doc(
                    "app.main",
                    meta_extra={"import_bindings": [{"module_id": "pytra.std.time"}]},
                )
            }

            with patch("toolchain2.link.runtime_discovery.resolve_runtime_east_path", return_value=str(bad_runtime)):
                with self.assertRaisesRegex(RuntimeError, "failed to parse runtime EAST"):
                    discover_runtime_modules(module_map)

    def test_runtime_discovery_allows_missing_speculative_runtime_submodule_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_path = Path(tmp) / "assertions.east"
            runtime_path.write_text(
                json.dumps(
                    _module_doc("pytra.utils.assertions"),
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            module_map = {
                "/tmp/app.main.east3.json": _module_doc(
                    "app.main",
                    body=[
                        {
                            "kind": "ImportFrom",
                            "module": "pytra.utils.assertions",
                            "names": [{"name": "py_assert_all"}],
                        }
                    ],
                )
            }

            def _resolve(module_id: str) -> str:
                if module_id == "pytra.utils.assertions":
                    return str(runtime_path)
                if module_id == "pytra.utils.assertions.py_assert_all":
                    return ""
                return ""

            with patch("toolchain2.link.runtime_discovery.resolve_runtime_east_path", side_effect=_resolve):
                result = discover_runtime_modules(module_map)

            self.assertIn(str(runtime_path), result)

    def test_manifest_loader_rejects_invalid_module_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema": "pytra.link_output.v1",
                        "target": "cpp",
                        "dispatch_mode": "native",
                        "entry_modules": ["app.main"],
                        "modules": [
                            {
                                "module_id": "app.main",
                                "input": "raw/app.main.east3.json",
                                "source_path": "app/main.py",
                                "is_entry": True,
                                "module_kind": "user",
                            }
                        ],
                        "global": {
                            "type_id_table": {},
                            "type_id_base_map": {},
                            "call_graph": {},
                            "sccs": [],
                            "non_escape_summary": {},
                            "container_ownership_hints_v1": {},
                        },
                        "diagnostics": {"warnings": [], "errors": []},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, r"manifest\.modules\[0\]\.output must be non-empty string"):
                load_linked_output(manifest_path)

    def test_manifest_loader_rejects_missing_linked_east_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema": "pytra.link_output.v1",
                        "target": "cpp",
                        "dispatch_mode": "native",
                        "entry_modules": ["app.main"],
                        "modules": [
                            {
                                "module_id": "app.main",
                                "input": "raw/app.main.east3.json",
                                "output": "east3/app.main.east3.json",
                                "source_path": "app/main.py",
                                "is_entry": True,
                                "module_kind": "user",
                            }
                        ],
                        "global": {
                            "type_id_table": {},
                            "type_id_base_map": {},
                            "call_graph": {},
                            "sccs": [],
                            "non_escape_summary": {},
                            "container_ownership_hints_v1": {},
                        },
                        "diagnostics": {"warnings": [], "errors": []},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "linked EAST file not found"):
                load_linked_output(manifest_path)

    def test_manifest_loader_rejects_invalid_linked_east_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            east_path = Path(tmp) / "east3" / "app.main.east3.json"
            east_path.parent.mkdir(parents=True, exist_ok=True)
            east_path.write_text("{bad json", encoding="utf-8")
            manifest_path = Path(tmp) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema": "pytra.link_output.v1",
                        "target": "cpp",
                        "dispatch_mode": "native",
                        "entry_modules": ["app.main"],
                        "modules": [
                            {
                                "module_id": "app.main",
                                "input": "raw/app.main.east3.json",
                                "output": "east3/app.main.east3.json",
                                "source_path": "app/main.py",
                                "is_entry": True,
                                "module_kind": "user",
                            }
                        ],
                        "global": {
                            "type_id_table": {},
                            "type_id_base_map": {},
                            "call_graph": {},
                            "sccs": [],
                            "non_escape_summary": {},
                            "container_ownership_hints_v1": {},
                        },
                        "diagnostics": {"warnings": [], "errors": []},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "failed to parse linked EAST file"):
                load_linked_output(manifest_path)

    def test_link_modules_manifest_input_points_to_raw_east3_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            entry_path = Path(tmp) / "app.main.east3.json"
            entry_path.write_text(
                json.dumps(
                    _module_doc(
                        "app.main",
                        source_path="app/main.py",
                    ),
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = link_modules([str(entry_path)], target="cpp", dispatch_mode="native")

            modules = result.manifest.get("modules")
            self.assertIsInstance(modules, list)
            assert isinstance(modules, list)
            entry = next(item for item in modules if isinstance(item, dict) and item.get("module_id") == "app.main")
            self.assertEqual(entry.get("input"), str(entry_path.resolve()))
            self.assertEqual(entry.get("source_path"), "app/main.py")

    def test_expand_defaults_uses_same_module_qualified_name(self) -> None:
        doc = _module_doc(
            "app.main",
            body=[
                {
                    "kind": "FunctionDef",
                    "name": "foo",
                    "arg_order": ["x", "y"],
                    "arg_defaults": {
                        "y": {"kind": "Constant", "value": 2},
                    },
                    "body": [],
                },
                {
                    "kind": "Expr",
                    "value": {
                        "kind": "Call",
                        "func": {"kind": "Name", "id": "foo"},
                        "args": [{"kind": "Constant", "value": 1}],
                    },
                },
            ],
        )

        expand_cross_module_defaults([doc])

        body = doc["body"]
        assert isinstance(body, list)
        call = body[1]["value"]
        self.assertEqual(len(call["args"]), 2)
        self.assertEqual(call["args"][1]["value"], 2)

    def test_expand_defaults_uses_imported_symbol_module_id(self) -> None:
        dep_doc = _module_doc(
            "pkg.dep",
            body=[
                {
                    "kind": "FunctionDef",
                    "name": "foo",
                    "arg_order": ["x", "y"],
                    "arg_defaults": {
                        "y": {"kind": "Constant", "value": 9},
                    },
                    "body": [],
                }
            ],
        )
        main_doc = _module_doc(
            "app.main",
            meta_extra={
                "import_symbols": {
                    "foo": {"module": "pkg.dep", "name": "foo"},
                }
            },
            body=[
                {
                    "kind": "Expr",
                    "value": {
                        "kind": "Call",
                        "func": {"kind": "Name", "id": "foo"},
                        "args": [{"kind": "Constant", "value": 1}],
                    },
                }
            ],
        )

        expand_cross_module_defaults([dep_doc, main_doc])

        body = main_doc["body"]
        assert isinstance(body, list)
        call = body[0]["value"]
        self.assertEqual(len(call["args"]), 2)
        self.assertEqual(call["args"][1]["value"], 9)

    def test_expand_defaults_does_not_expand_ambiguous_object_method_calls(self) -> None:
        doc_a = _module_doc(
            "pkg.a",
            body=[
                {
                    "kind": "ClassDef",
                    "name": "A",
                    "body": [
                        {
                            "kind": "FunctionDef",
                            "name": "run",
                            "arg_order": ["self", "x", "y"],
                            "arg_defaults": {
                                "y": {"kind": "Constant", "value": 1},
                            },
                            "body": [],
                        }
                    ],
                }
            ],
        )
        doc_b = _module_doc(
            "pkg.b",
            body=[
                {
                    "kind": "ClassDef",
                    "name": "B",
                    "body": [
                        {
                            "kind": "FunctionDef",
                            "name": "run",
                            "arg_order": ["self", "x", "y"],
                            "arg_defaults": {
                                "y": {"kind": "Constant", "value": 2},
                            },
                            "body": [],
                        }
                    ],
                }
            ],
        )
        main_doc = _module_doc(
            "app.main",
            body=[
                {
                    "kind": "Expr",
                    "value": {
                        "kind": "Call",
                        "func": {
                            "kind": "Attribute",
                            "value": {"kind": "Name", "id": "obj"},
                            "attr": "run",
                        },
                        "args": [{"kind": "Constant", "value": 3}],
                    },
                }
            ],
        )

        expand_cross_module_defaults([doc_a, doc_b, main_doc])

        body = main_doc["body"]
        assert isinstance(body, list)
        call = body[0]["value"]
        self.assertEqual(len(call["args"]), 1)


if __name__ == "__main__":
    unittest.main()
