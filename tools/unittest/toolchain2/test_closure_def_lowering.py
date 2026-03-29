from __future__ import annotations

import unittest
from pathlib import Path

from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.emit.cpp.emitter import emit_cpp_module
from toolchain2.emit.go.emitter import emit_go_module
from toolchain2.parse.py.parse_python import parse_python_file
from toolchain2.resolve.py.builtin_registry import load_builtin_registry
from toolchain2.resolve.py.resolver import resolve_east1_to_east2


ROOT = Path(__file__).resolve().parents[3]


def _build_east3_for(path: Path) -> dict:
    builtins_path = ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1"
    containers_path = ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1"
    stdlib_dir = ROOT / "test" / "include" / "east1" / "py" / "std"
    registry = load_builtin_registry(builtins_path, containers_path, stdlib_dir)
    east1 = parse_python_file(str(path))
    resolve_east1_to_east2(east1, registry=registry)
    return lower_east2_to_east3(east1)


def _find_function(body: list[object], name: str, kind: str) -> dict:
    for stmt in body:
        if isinstance(stmt, dict) and stmt.get("kind") == kind and stmt.get("name") == name:
            return stmt
    raise AssertionError(f"missing {kind} {name}")


class ClosureDefLoweringTests(unittest.TestCase):
    def test_nested_function_defs_lower_to_closure_defs_with_captures(self) -> None:
        east3 = _build_east3_for(ROOT / "test" / "fixtures" / "control" / "nested_closure_def.py")

        outer = _find_function(east3["body"], "outer", "FunctionDef")
        inner = _find_function(outer["body"], "inner", "ClosureDef")
        rec = _find_function(outer["body"], "rec", "ClosureDef")

        self.assertEqual(inner["capture_modes"], {"scale": "readonly", "x": "mutable"})
        self.assertEqual(rec["capture_modes"], {"bump": "readonly"})
        self.assertEqual([capture["name"] for capture in inner["captures"]], ["scale", "x"])
        self.assertTrue(rec.get("is_recursive"))

    def test_go_and_cpp_emitters_map_closure_defs(self) -> None:
        east3 = _build_east3_for(ROOT / "test" / "fixtures" / "control" / "nested_closure_def.py")

        go_code = emit_go_module(east3)
        cpp_code = emit_cpp_module(east3)

        self.assertIn("inner := func(y int64) int64 {", go_code)
        self.assertIn("var rec func(n int64) int64", go_code)
        self.assertIn("rec = func(n int64) int64 {", go_code)
        self.assertIn("::std::function<int64(int64)> inner = [&](int64 y) -> int64 {", cpp_code)
        self.assertIn("::std::function<int64(int64)> rec = [&](int64 n) -> int64 {", cpp_code)


if __name__ == "__main__":
    unittest.main()
