"""Unit tests for EAST3 default argument expansion pass."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from src.toolchain.compile.core_entrypoints import convert_source_to_east_with_backend
from src.toolchain.compile.east2_to_east3_lowering import lower_east2_to_east3


def _build_east3(source: str) -> dict[str, object]:
    east = convert_source_to_east_with_backend(
        source, filename="test.py", parser_backend="self_hosted",
    )
    return lower_east2_to_east3(east)


def _find_calls(node: object, func_name: str) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    if isinstance(node, dict):
        if node.get("kind") == "Call":
            func = node.get("func", {})
            if isinstance(func, dict) and func.get("id") == func_name:
                results.append(node)
        for v in node.values():
            results.extend(_find_calls(v, func_name))
    elif isinstance(node, list):
        for item in node:
            results.extend(_find_calls(item, func_name))
    return results


class TestDefaultArgExpansion(unittest.TestCase):

    def test_missing_defaults_are_expanded(self) -> None:
        source = """def greet(name: str, greeting: str = "Hello", times: int = 1) -> str:
    return greeting + " " + name

def main() -> None:
    greet("World")
"""
        east3 = _build_east3(source)
        calls = _find_calls(east3, "greet")
        self.assertTrue(len(calls) > 0)
        args = calls[0].get("args", [])
        self.assertEqual(len(args), 3)
        # arg[1] should be "Hello"
        self.assertEqual(args[1].get("value"), "Hello")
        # arg[2] should be 1
        self.assertEqual(args[2].get("value"), 1)

    def test_partial_defaults_expanded(self) -> None:
        source = """def foo(a: int, b: int = 10, c: int = 20) -> int:
    return a + b + c

def main() -> None:
    foo(1, 2)
"""
        east3 = _build_east3(source)
        calls = _find_calls(east3, "foo")
        self.assertTrue(len(calls) > 0)
        args = calls[0].get("args", [])
        self.assertEqual(len(args), 3)
        # a=1, b=2 (explicit), c=20 (default)
        self.assertEqual(args[0].get("value"), 1)
        self.assertEqual(args[1].get("value"), 2)
        self.assertEqual(args[2].get("value"), 20)

    def test_all_args_provided_no_change(self) -> None:
        source = """def foo(a: int, b: int = 10) -> int:
    return a + b

def main() -> None:
    foo(1, 2)
"""
        east3 = _build_east3(source)
        calls = _find_calls(east3, "foo")
        self.assertTrue(len(calls) > 0)
        args = calls[0].get("args", [])
        self.assertEqual(len(args), 2)

    def test_no_defaults_no_change(self) -> None:
        source = """def foo(a: int, b: int) -> int:
    return a + b

def main() -> None:
    foo(1, 2)
"""
        east3 = _build_east3(source)
        calls = _find_calls(east3, "foo")
        self.assertTrue(len(calls) > 0)
        args = calls[0].get("args", [])
        self.assertEqual(len(args), 2)

    def test_method_with_self_excluded(self) -> None:
        source = """class Greeter:
    def greet(self, name: str, greeting: str = "Hi") -> str:
        return greeting + " " + name

def main() -> None:
    g = Greeter()
    g.greet("World")
"""
        east3 = _build_east3(source)
        calls = _find_calls(east3, "greet")
        # Method call args should have name + greeting (self excluded from count)
        for call in calls:
            args = call.get("args", [])
            # Should have at least 2 args after expansion (name + greeting default)
            self.assertGreaterEqual(len(args), 2)


if __name__ == "__main__":
    unittest.main()
