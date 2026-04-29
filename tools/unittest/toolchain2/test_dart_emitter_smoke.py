from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from toolchain.compile.lower import lower_east2_to_east3
from toolchain.emit.dart.cli import _copy_dart_runtime
from toolchain.emit.dart.emitter import emit_dart_module
from toolchain.parse.py.parser import parse_python_source
from toolchain.resolve.py.builtin_registry import load_builtin_registry
from toolchain.resolve.py.resolver import resolve_east1_to_east2


ROOT = Path(__file__).resolve().parents[3]


def _load_registry():
    return load_builtin_registry(
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "std",
    )


def _build_east3(source: str) -> dict:
    east2 = parse_python_source(source, "<dart-smoke>").to_jv()
    resolve_east1_to_east2(east2, registry=_load_registry())
    east3 = lower_east2_to_east3(east2, target_language="dart")
    meta = east3.setdefault("meta", {})
    assert isinstance(meta, dict)
    meta["emit_context"] = {"module_id": "app", "root_rel_prefix": "./", "is_entry": True}
    return east3


def _assert_dart_runs(source: str) -> str:
    if shutil.which("dart") is None:
        raise unittest.SkipTest("dart is not installed")
    east3 = _build_east3(source)
    dart_code = emit_dart_module(east3)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        app_path = tmp_path / "app.dart"
        runtime_root = ROOT / "src" / "runtime" / "dart"
        built_in_dir = tmp_path / "built_in"
        std_dir = tmp_path / "std"
        built_in_dir.mkdir(parents=True, exist_ok=True)
        std_dir.mkdir(parents=True, exist_ok=True)
        for src in runtime_root.joinpath("built_in").glob("*.dart"):
            shutil.copy2(src, built_in_dir / src.name)
        for src in runtime_root.joinpath("std").glob("*.dart"):
            shutil.copy2(src, std_dir / src.name)
        app_path.write_text(dart_code, encoding="utf-8")
        run = subprocess.run(
            ["dart", "run", str(app_path)],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
    if run.returncode != 0:
        raise AssertionError(f"{run.stdout}\n{run.stderr}")
    return run.stdout


class DartEmitterSmokeTest(unittest.TestCase):
    def test_cli_runtime_copy_provides_import_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            _copy_dart_runtime(out_dir)
            self.assertTrue((out_dir / "built_in" / "py_runtime.dart").exists())
            self.assertTrue((out_dir / "std" / "sys_native.dart").exists())

    def test_emit_add_function(self) -> None:
        source = """
def add(a: int, b: int) -> int:
    return a + b
"""
        east3 = _build_east3(source)
        code = emit_dart_module(east3)
        self.assertIn("int add(", code)
        self.assertIn("return pytraInt((a + b));", code)

    def test_emit_if_else(self) -> None:
        source = """
def f(x: int) -> int:
    if x < 1:
        return 10
    return 20
"""
        east3 = _build_east3(source)
        code = emit_dart_module(east3)
        self.assertIn("if ((x < 1))", code)
        self.assertIn("return 10;", code)

    def test_import_bindings_emit_linked_user_symbol_import(self) -> None:
        east3 = {
            "kind": "Module",
            "east_stage": 3,
            "body": [],
            "meta": {
                "_cli_all_module_ids": ["toolchain.emit.common.cli_runner"],
                "import_bindings": [
                    {
                        "module_id": "toolchain.emit.common.cli_runner",
                        "runtime_module_id": "toolchain.emit.common.cli_runner",
                        "export_name": "run_emit_cli",
                        "local_name": "run_emit_cli",
                        "binding_kind": "symbol",
                    }
                ],
                "emit_context": {"module_id": "toolchain.emit.cpp.cli", "root_rel_prefix": "./", "is_entry": True},
            },
        }
        code = emit_dart_module(east3)

        self.assertIn("import './toolchain/emit/common/cli_runner.dart' as __mod_cli_runner;", code)

    def test_emit_tuple_unpack_stmt(self) -> None:
        east3 = {
            "kind": "Module",
            "east_stage": 3,
            "body": [
                {
                    "kind": "FunctionDef",
                    "name": "pair",
                    "args": [],
                    "arg_types": {},
                    "return_type": "tuple[int64,int64]",
                    "body": [
                        {
                            "kind": "Return",
                            "value": {
                                "kind": "Tuple",
                                "elements": [
                                    {"kind": "Constant", "value": 1, "resolved_type": "int64"},
                                    {"kind": "Constant", "value": 2, "resolved_type": "int64"},
                                ],
                                "resolved_type": "tuple[int64,int64]",
                            },
                        }
                    ],
                },
                {
                    "kind": "FunctionDef",
                    "name": "f",
                    "args": [],
                    "arg_types": {},
                    "return_type": "int64",
                    "body": [
                        {
                            "kind": "TupleUnpack",
                            "declare": True,
                            "targets": [
                                {"kind": "Name", "id": "x", "resolved_type": "int64"},
                                {"kind": "Name", "id": "y", "resolved_type": "int64"},
                            ],
                            "value": {
                                "kind": "Call",
                                "func": {"kind": "Name", "id": "pair"},
                                "args": [],
                                "resolved_type": "tuple[int64,int64]",
                            },
                        },
                        {
                            "kind": "Return",
                            "value": {
                                "kind": "BinOp",
                                "left": {"kind": "Name", "id": "x", "resolved_type": "int64"},
                                "op": "Add",
                                "right": {"kind": "Name", "id": "y", "resolved_type": "int64"},
                                "resolved_type": "int64",
                            },
                        },
                    ],
                },
            ],
            "meta": {"emit_context": {"module_id": "app", "root_rel_prefix": "./", "is_entry": True}},
        }
        code = emit_dart_module(east3)
        self.assertIn("var __pytraTuple_", code)
        self.assertIn("var x = __pytraTuple_", code)
        self.assertIn("var y = __pytraTuple_", code)

    def test_emit_and_run_print(self) -> None:
        out = _assert_dart_runs(
            """
def f() -> int:
    return 3

if __name__ == "__main__":
    print(f())
"""
        )
        self.assertEqual(out.strip(), "3")
