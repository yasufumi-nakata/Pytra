from __future__ import annotations

import unittest
from pathlib import Path

from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.emit.cpp.emitter import emit_cpp_module
from toolchain2.emit.go.emitter import emit_go_module
from toolchain2.parse.py.parser import parse_python_source
from toolchain2.resolve.py.builtin_registry import load_builtin_registry
from toolchain2.resolve.py.resolver import resolve_east1_to_east2


ROOT = Path(__file__).resolve().parents[3]


def _load_registry():
    return load_builtin_registry(
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "std",
    )


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


def _build_east3(source: str, *, target_language: str) -> dict:
    east2 = parse_python_source(source, "<mem>").to_jv()
    resolve_east1_to_east2(east2, registry=_load_registry())
    return lower_east2_to_east3(east2, target_language=target_language)


class TupleUnpackLoweringProfileTests(unittest.TestCase):
    def test_go_profile_lowers_tuple_assign_to_multi_assign(self) -> None:
        east3 = _build_east3(
            """
def pair() -> tuple[int, int]:
    return 1, 2

def f() -> int:
    x, y = pair()
    return x + y
""",
            target_language="go",
        )

        multi_assign = next(node for node in _walk(east3) if node.get("kind") == "MultiAssign")
        go_code = emit_go_module(east3)

        self.assertEqual(multi_assign.get("kind"), "MultiAssign")
        self.assertEqual(multi_assign.get("target_types"), ["int64", "int64"])
        self.assertTrue(multi_assign.get("declare"))
        self.assertEqual(multi_assign.get("value", {}).get("kind"), "Call")
        self.assertIn("func pair() (int64, int64) {", go_code)
        self.assertIn("return int64(1), int64(2)", go_code)
        self.assertIn("x, y := pair()", go_code)

        pair_fn = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "FunctionDef" and node.get("name") == "pair"
        )
        self.assertEqual(pair_fn.get("return_type"), "multi_return[int64,int64]")

    def test_cpp_profile_lowers_tuple_assign_to_tuple_unpack(self) -> None:
        east3 = _build_east3(
            """
def pair() -> tuple[int, int]:
    return 1, 2

def f() -> int:
    x, y = pair()
    return x + y
""",
            target_language="cpp",
        )

        tuple_unpack = next(node for node in _walk(east3) if node.get("kind") == "TupleUnpack")
        cpp_code = emit_cpp_module(east3)

        self.assertEqual(tuple_unpack.get("target_types"), ["int64", "int64"])
        self.assertTrue(tuple_unpack.get("declare"))
        self.assertEqual(tuple_unpack.get("value", {}).get("kind"), "Call")
        self.assertIn("::std::tuple<int64, int64> __tup_1 = pair();", cpp_code)
        self.assertIn("int64 x = ::std::get<0>(__tup_1);", cpp_code)

        pair_fn = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "FunctionDef" and node.get("name") == "pair"
        )
        self.assertEqual(pair_fn.get("return_type"), "tuple[int64,int64]")

    def test_core_profile_keeps_temp_subscript_expansion(self) -> None:
        east3 = _build_east3(
            """
def pair() -> tuple[int, int]:
    return 1, 2

def f() -> int:
    x, y = pair()
    return x + y
""",
            target_language="core",
        )

        tmp_assign = next(
            node
            for node in _walk(east3)
            if node.get("kind") == "Assign"
            and isinstance(node.get("target"), dict)
            and node["target"].get("id") == "__tup_1"
        )

        self.assertEqual(tmp_assign.get("decl_type"), "tuple[int64,int64]")
        self.assertFalse(any(node.get("kind") == "TupleUnpack" for node in _walk(east3)))
        self.assertFalse(any(node.get("kind") == "MultiAssign" for node in _walk(east3)))


if __name__ == "__main__":
    unittest.main()
