from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from toolchain2.common.jv import deep_copy_json
from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.parse.py.parser import parse_python_source
from toolchain2.resolve.py.builtin_registry import BuiltinRegistry, load_builtin_registry
from toolchain2.resolve.py.resolver import resolve_east1_to_east2
from toolchain2.resolve.py.validate_east2 import validate_east2


def _walk(node: object) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    if isinstance(node, dict):
        out.append(node)
        for value in node.values():
            out.extend(_walk(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_walk(item))
    return out


def _load_registry() -> BuiltinRegistry:
    return load_builtin_registry(
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "std",
    )


class Toolchain2SpecConformTests(unittest.TestCase):
    def test_parser_preserves_typing_prefix_until_resolve(self) -> None:
        source = """
import typing

def f(xs: typing.List[int], *rest: typing.Tuple[str, int]) -> "typing.List[int]":
    return xs
"""
        east1 = parse_python_source(source, "<mem>").to_jv()
        fn = next(node for node in _walk(east1) if node.get("kind") == "FunctionDef" and node.get("name") == "f")

        self.assertEqual(fn.get("arg_types", {}).get("xs"), "typing.List[int]")
        self.assertEqual(fn.get("vararg_type"), "typing.Tuple[str, int]")
        self.assertEqual(fn.get("return_type"), '"typing.List[int]"')

        east2 = deep_copy_json(east1)
        self.assertIsInstance(east2, dict)
        resolve_east1_to_east2(east2, registry=_load_registry())
        fn2 = next(node for node in _walk(east2) if node.get("kind") == "FunctionDef" and node.get("name") == "f")

        self.assertEqual(fn2.get("arg_types", {}).get("xs"), "list[int64]")
        self.assertEqual(fn2.get("vararg_type"), "tuple[str,int64]")
        self.assertEqual(fn2.get("return_type"), "list[int64]")
        self.assertEqual(
            fn2.get("vararg_type_expr"),
            {
                "kind": "GenericType",
                "base": "tuple",
                "args": [
                    {"kind": "NamedType", "name": "str"},
                    {"kind": "NamedType", "name": "int64"},
                ],
            },
        )

    def test_parser_preserves_type_alias_value_in_east1(self) -> None:
        source = """
type Scalar = int | float
"""
        east1 = parse_python_source(source, "<mem>").to_jv()

        type_alias = next(node for node in _walk(east1) if node.get("kind") == "TypeAlias")
        self.assertEqual(type_alias.get("name"), "Scalar")
        self.assertEqual(type_alias.get("value"), "int | float")

    def test_resolver_expands_type_aliases_by_east2(self) -> None:
        source = """
type Scalar = int | float

def identity(value: Scalar) -> Scalar:
    return value
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())

        type_alias = next(node for node in _walk(east2) if node.get("kind") == "TypeAlias")
        fn = next(node for node in _walk(east2) if node.get("kind") == "FunctionDef" and node.get("name") == "identity")
        ret_name = next(
            node for node in _walk(fn)
            if node.get("kind") == "Name" and node.get("id") == "value" and node.get("resolved_type") != "callable"
        )

        self.assertEqual(type_alias.get("value"), "int64 | float64")
        self.assertEqual(fn.get("arg_types", {}).get("value"), "int64 | float64")
        self.assertEqual(fn.get("return_type"), "int64 | float64")
        self.assertEqual(ret_name.get("resolved_type"), "int64 | float64")

    def test_registry_driven_resolution_covers_builtins_stdlib_and_forrange(self) -> None:
        source = """
from pytra.std import json, random
from pytra.std.pathlib import Path

def f(xs: list[int], ys: list[str], text: str) -> None:
    a = sorted(xs)
    b = zip(xs, ys)
    c = json.loads(text)
    d = random.randint(1, 2)
    p = Path("x")
    for i in range(3):
        pass
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())

        sorted_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Name"
            and node["func"].get("id") == "sorted"
        )
        zip_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Name"
            and node["func"].get("id") == "zip"
        )
        json_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Attribute"
            and isinstance(node["func"].get("value"), dict)
            and node["func"]["value"].get("kind") == "Name"
            and node["func"]["value"].get("id") == "json"
            and node["func"].get("attr") == "loads"
        )
        randint_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Attribute"
            and isinstance(node["func"].get("value"), dict)
            and node["func"]["value"].get("kind") == "Name"
            and node["func"]["value"].get("id") == "random"
            and node["func"].get("attr") == "randint"
        )
        path_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Name"
            and node["func"].get("id") == "Path"
        )
        for_range = next(node for node in _walk(east2) if node.get("kind") == "ForRange")

        self.assertEqual(sorted_call.get("resolved_type"), "list[int64]")
        self.assertEqual(zip_call.get("resolved_type"), "list[tuple[int64,str]]")
        self.assertEqual(json_call.get("resolved_type"), "JsonValue")
        self.assertEqual(json_call.get("runtime_module_id"), "pytra.std.json")
        self.assertEqual(randint_call.get("resolved_type"), "int64")
        self.assertEqual(randint_call.get("runtime_module_id"), "pytra.std.random")
        self.assertEqual(path_call.get("resolved_type"), "Path")
        self.assertEqual(for_range.get("target_type"), "int64")
        self.assertEqual(for_range.get("target", {}).get("resolved_type"), "int64")

    def test_resolve_requires_registry(self) -> None:
        east1 = parse_python_source("def f() -> None:\n    pass\n", "<mem>").to_jv()
        with self.assertRaisesRegex(ValueError, "registry is required"):
            resolve_east1_to_east2(east1, registry=None)

    def test_resolver_keeps_pathlib_methods_transpilable_and_resolves_with_body(self) -> None:
        source = """
from pytra.std.pathlib import Path

def f(p: Path) -> str:
    p.write_text("42")
    with open("out.bin", "wb") as fh:
        fh.write(bytes(bytearray([1, 2, 3])))
    return p.read_text()
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())

        write_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Attribute"
            and node["func"].get("attr") == "write_text"
        )
        read_call = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "Call"
            and isinstance(node.get("func"), dict)
            and node["func"].get("kind") == "Attribute"
            and node["func"].get("attr") == "read_text"
        )
        with_node = next(node for node in _walk(east2) if node.get("kind") == "With")
        with_body_call = with_node["body"][0]["value"]

        self.assertNotEqual(write_call.get("lowered_kind"), "BuiltinCall")
        self.assertNotEqual(read_call.get("lowered_kind"), "BuiltinCall")
        self.assertEqual(with_node.get("context_expr", {}).get("kind"), "Call")
        self.assertEqual(with_node.get("context_expr", {}).get("args", [])[0].get("resolved_type"), "str")
        self.assertEqual(with_body_call.get("args", [])[0].get("resolved_type"), "bytes")

    def test_boolop_value_select_preserves_operand_type(self) -> None:
        source = """
def f() -> None:
    x: str = ""
    y: str = "fallback"
    z: str = x or y
    n: int = 0
    m: int = 9
    t: int = n or m
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())

        boolops = [node for node in _walk(east2) if node.get("kind") == "BoolOp"]
        self.assertEqual(len(boolops), 2)
        self.assertEqual(boolops[0].get("resolved_type"), "str")
        self.assertEqual(boolops[1].get("resolved_type"), "int64")

    def test_ann_assign_does_not_rewrite_any_annotated_value_type(self) -> None:
        source = """
from pytra.typing import Any

def f() -> None:
    values: list[Any] = [1, 2]
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())

        ann_assign = next(
            node
            for node in _walk(east2)
            if node.get("kind") == "AnnAssign"
            and isinstance(node.get("target"), dict)
            and node["target"].get("id") == "values"
        )

        self.assertEqual(ann_assign.get("decl_type"), "list[Any]")
        self.assertEqual(ann_assign.get("value", {}).get("resolved_type"), "list[int64]")

        east3 = lower_east2_to_east3(east2)
        ann_assign3 = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "AnnAssign"
            and isinstance(node.get("target"), dict)
            and node["target"].get("id") == "values"
        )
        self.assertEqual(ann_assign3.get("value", {}).get("kind"), "Box")
        self.assertEqual(ann_assign3.get("value", {}).get("target"), "list[Any]")

    def test_compile_inserts_unbox_for_yields_dynamic_assignment_targets(self) -> None:
        source = """
from pytra.typing import Any

def f(root: dict[str, Any]) -> int:
    meta: dict[str, Any] = root.get("meta", {})
    total: int = 0
    for _k, v in meta.items():
        total += v
    return total
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2)

        meta_assign = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "AnnAssign"
            and isinstance(node.get("target"), dict)
            and node["target"].get("id") == "meta"
        )
        total_aug = next(node for node in _walk(east3) if node.get("kind") == "AugAssign")

        self.assertEqual(meta_assign.get("value", {}).get("kind"), "Unbox")
        self.assertEqual(meta_assign.get("value", {}).get("target"), "dict[str,Any]")
        self.assertEqual(total_aug.get("value", {}).get("kind"), "Unbox")
        self.assertEqual(total_aug.get("value", {}).get("target"), "int64")

    def test_compile_keeps_optional_unbox_boundary_for_dict_get_without_default(self) -> None:
        source = """
def f(d: dict[str, int]) -> bool:
    g: int | None = d.get("x")
    return g is not None
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2)

        g_assign = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "AnnAssign"
            and isinstance(node.get("target"), dict)
            and node["target"].get("id") == "g"
        )

        self.assertEqual(g_assign.get("decl_type"), "int64 | None")
        self.assertEqual(g_assign.get("value", {}).get("kind"), "Unbox")
        self.assertEqual(g_assign.get("value", {}).get("target"), "int64 | None")
        self.assertTrue(g_assign.get("value", {}).get("value", {}).get("yields_dynamic"))

    def test_compile_narrows_union_names_inside_isinstance_guard(self) -> None:
        source = """
type Scalar = int | float

def add_scalars(a: Scalar, b: Scalar) -> int:
    if isinstance(a, int) and isinstance(b, int):
        return a + b
    return 0
"""
        east2 = parse_python_source(source, "<mem>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2)

        guarded_return = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "Return"
            and isinstance(node.get("value"), dict)
            and node["value"].get("kind") == "BinOp"
        )
        binop = guarded_return["value"]
        left = binop.get("left", {})
        right = binop.get("right", {})

        self.assertEqual(left.get("kind"), "Unbox")
        self.assertEqual(left.get("target"), "int64")
        self.assertEqual(right.get("kind"), "Unbox")
        self.assertEqual(right.get("target"), "int64")
        self.assertEqual(binop.get("resolved_type"), "int64")

    def test_validator_reports_unknown_missing_and_unnormalized_types(self) -> None:
        unknown_doc = {
            "kind": "Module",
            "east_stage": 2,
            "schema_version": 1,
            "source_path": "<unknown>",
            "meta": {"dispatch_mode": "native"},
            "body": [
                {
                    "kind": "Expr",
                    "value": {
                        "kind": "Name",
                        "id": "x",
                        "resolved_type": "unknown",
                    },
                }
            ],
        }
        missing_doc = {
            "kind": "Module",
            "east_stage": 2,
            "schema_version": 1,
            "source_path": "<missing>",
            "meta": {"dispatch_mode": "native"},
            "body": [
                {
                    "kind": "Expr",
                    "value": {
                        "kind": "Name",
                        "id": "x",
                    },
                }
            ],
        }
        range_doc = {
            "kind": "Module",
            "east_stage": 2,
            "schema_version": 1,
            "source_path": "<range>",
            "meta": {"dispatch_mode": "native"},
            "body": [
                {
                    "kind": "FunctionDef",
                    "name": "f",
                    "arg_types": {"x": "int"},
                    "arg_usage": {"x": "readonly"},
                    "arg_type_exprs": {"x": {"kind": "NamedType", "name": "int64"}},
                    "return_type": "float",
                    "return_type_expr": {"kind": "NamedType", "name": "float64"},
                    "body": [
                        {
                            "kind": "Expr",
                            "value": {
                                "kind": "RangeExpr",
                                "resolved_type": "list[int64]",
                                "start": {"kind": "Constant", "value": 0, "resolved_type": "int64"},
                                "stop": {"kind": "Constant", "value": 3, "resolved_type": "int64"},
                                "step": {"kind": "Constant", "value": 1, "resolved_type": "int64"},
                            },
                        }
                    ],
                }
            ],
        }

        unknown_result = validate_east2(unknown_doc)
        missing_result = validate_east2(missing_doc)
        range_result = validate_east2(range_doc)

        self.assertTrue(any("resolved_type is unknown" in err for err in unknown_result.errors))
        self.assertTrue(any("missing resolved_type" in err for err in missing_result.errors))
        self.assertTrue(any("unnormalized type 'int'" in err for err in range_result.errors))
        self.assertTrue(any("unnormalized type 'float'" in err for err in range_result.errors))
        self.assertFalse(any("RangeExpr" in err for err in range_result.errors))


if __name__ == "__main__":
    unittest.main()
