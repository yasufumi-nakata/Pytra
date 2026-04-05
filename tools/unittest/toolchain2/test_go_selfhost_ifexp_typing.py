from __future__ import annotations

import unittest
from pathlib import Path

from toolchain.compile.lower import lower_east2_to_east3
from toolchain.emit.go.emitter import emit_go_module
from toolchain.parse.py.parse_python import parse_python_file
from toolchain.resolve.py.builtin_registry import load_builtin_registry
from toolchain.resolve.py.resolver import resolve_east1_to_east2


ROOT = Path(__file__).resolve().parents[3]


def _build_east3_for(path: Path) -> dict:
    builtins_path = ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1"
    containers_path = ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1"
    stdlib_dir = ROOT / "test" / "include" / "east1" / "py" / "std"
    registry = load_builtin_registry(builtins_path, containers_path, stdlib_dir)
    east1 = parse_python_file(str(path))
    resolve_east1_to_east2(east1, registry=registry)
    return lower_east2_to_east3(east1)


class GoSelfhostIfExpTypingTests(unittest.TestCase):
    def test_go_emitter_emits_type_alias_declarations(self) -> None:
        east3 = _build_east3_for(ROOT / "src" / "pytra" / "std" / "json.py")

        go_code = emit_go_module(east3)

        self.assertIn("type JsonVal = any", go_code)

    def test_selfhost_emitter_coerces_isinstance_guarded_jsonval_ternaries(self) -> None:
        east3 = _build_east3_for(ROOT / "src" / "toolchain" / "emit" / "go" / "emitter.py")

        go_code = emit_go_module(east3)

        self.assertIn('py_ternary_str(py_is_str(a), a.(string), "")', go_code)
        self.assertTrue(
            'py_ternary_int(py_is_int(v), py_to_int64(v), 0)' in go_code
            or 'py_ternary_int(py_is_exact_int64(v), py_to_int64(v), int64(0))' in go_code
        )
        self.assertNotIn('func() *JsonVal { if py_is_str(a) { return a }; return "" }()', go_code)
        self.assertNotIn('func() *JsonVal { if py_is_int(v) { return v }; return 0 }()', go_code)


if __name__ == "__main__":
    unittest.main()
