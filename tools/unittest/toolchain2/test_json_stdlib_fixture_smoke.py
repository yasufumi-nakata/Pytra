from __future__ import annotations

import unittest
from pathlib import Path

from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.parse.py.parse_python import parse_python_file
from toolchain2.resolve.py.builtin_registry import load_builtin_registry
from toolchain2.resolve.py.resolver import resolve_east1_to_east2


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = ROOT / "test" / "fixture" / "source" / "py" / "stdlib"


def _load_registry():
    return load_builtin_registry(
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "std",
    )


class JsonStdlibFixtureSmokeTests(unittest.TestCase):
    def test_json_unicode_escape_fixture_parses_and_lowers(self) -> None:
        path = FIXTURE_ROOT / "json_unicode_escape.py"
        east1 = parse_python_file(str(path))
        east1["source_path"] = "test/fixture/source/py/stdlib/json_unicode_escape.py"
        resolve_east1_to_east2(east1, registry=_load_registry())
        east3 = lower_east2_to_east3(east1, target_language="go")
        self.assertEqual(east3.get("kind"), "Module")
        self.assertIn("body", east3)

    def test_json_indent_optional_fixture_parses_and_lowers(self) -> None:
        path = FIXTURE_ROOT / "json_indent_optional.py"
        east1 = parse_python_file(str(path))
        east1["source_path"] = "test/fixture/source/py/stdlib/json_indent_optional.py"
        resolve_east1_to_east2(east1, registry=_load_registry())
        east3 = lower_east2_to_east3(east1, target_language="go")
        self.assertEqual(east3.get("kind"), "Module")
        self.assertIn("body", east3)


if __name__ == "__main__":
    unittest.main()
