from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from functools import lru_cache

from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.emit.go.emitter import emit_go_module
from toolchain2.parse.py.parser import parse_python_source
from toolchain2.resolve.py.builtin_registry import load_builtin_registry
from toolchain2.resolve.py.resolver import resolve_east1_to_east2


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = ROOT / "test" / "fixture" / "source" / "py"


def _load_registry():
    return load_builtin_registry(
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "std",
    )


@lru_cache(maxsize=1)
def _emit_builtin_error_go() -> str:
    source = (ROOT / "src" / "pytra" / "built_in" / "error.py").read_text(encoding="utf-8")
    east2 = parse_python_source(source, "<built-in-error>").to_jv()
    resolve_east1_to_east2(east2, registry=_load_registry())
    east3 = lower_east2_to_east3(east2, target_language="go")
    meta = east3.setdefault("meta", {})
    assert isinstance(meta, dict)
    meta["emit_context"] = {"module_id": "pytra.built_in.error", "is_entry": False}
    return emit_go_module(east3)


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


SOURCE = """
def parse_int(s: str) -> int:
    if not s.isdigit():
        raise ValueError("bad")
    return int(s)

def process(s: str) -> int:
    x = parse_int(s)
    return x

if __name__ == "__main__":
    try:
        print(process("7"))
    except ValueError as err:
        print(err)
"""

NESTED_RETURN_SOURCE = """
def parse_int(s: str) -> int:
    if not s.isdigit():
        raise ValueError("bad")
    return int(s)

def as_chr(s: str) -> str:
    return chr(parse_int(s))

if __name__ == "__main__":
    try:
        print(as_chr("7"))
        print(as_chr("x"))
    except ValueError as err:
        print(err)
"""

FIXTURE_SOURCE = (
    FIXTURE_ROOT / "typing" / "union_return_errorcheck.py"
).read_text(encoding="utf-8")


class GoUnionReturnLoweringTests(unittest.TestCase):
    def test_lowering_rewrites_raise_try_and_can_raise_calls(self) -> None:
        east2 = parse_python_source(SOURCE, "<go-union-return>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2, target_language="go")
        nodes = _walk(east3)
        kinds = [str(node.get("kind", "")) for node in nodes]
        self.assertIn("ErrorReturn", kinds)
        self.assertIn("ErrorCheck", kinds)
        self.assertIn("ErrorCatch", kinds)
        self.assertNotIn("Raise", kinds)
        self.assertNotIn("Try", kinds)

        body = east3.get("body", [])
        assert isinstance(body, list)
        parse_fn = body[0]
        process_fn = body[1]
        assert isinstance(parse_fn, dict)
        assert isinstance(process_fn, dict)
        self.assertEqual(parse_fn.get("return_type"), "multi_return[int64,Exception]")
        self.assertEqual(process_fn.get("return_type"), "multi_return[int64,Exception]")

    def test_go_union_return_smoke_runs_for_assignment_lane(self) -> None:
        source = """
def parse_int(s: str) -> int:
    if not s.isdigit():
        raise ValueError("bad")
    return int(s)

def process(s: str) -> int:
    x = parse_int(s)
    return x

if __name__ == "__main__":
    try:
        x = process("7")
        print(x)
        y = process("x")
        print(y)
    except ValueError as err:
        print(err)
"""
        east2 = parse_python_source(source, "<go-union-run>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2, target_language="go")
        meta = east3.setdefault("meta", {})
        assert isinstance(meta, dict)
        meta["emit_context"] = {"module_id": "app", "is_entry": True}
        go_code = emit_go_module(east3)
        env = dict(os.environ)
        env["PATH"] = "/home/node/.local/go/bin:" + env.get("PATH", "")
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "app.go").write_text(go_code, encoding="utf-8")
            (tmpdir / "py_runtime.go").write_text(
                (ROOT / "src" / "runtime" / "go" / "built_in" / "py_runtime.go").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (tmpdir / "pytra_built_in_error.go").write_text(_emit_builtin_error_go(), encoding="utf-8")
            build = subprocess.run(
                [
                    "go",
                    "build",
                    "-o",
                    str(tmpdir / "app"),
                    str(tmpdir / "py_runtime.go"),
                    str(tmpdir / "pytra_built_in_error.go"),
                    str(tmpdir / "app.go"),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(tmpdir / "app")], cwd=tmp, capture_output=True, text=True, env=env)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, "7\nbad\n")

    def test_lowering_hoists_error_check_for_nested_return_call(self) -> None:
        east2 = parse_python_source(NESTED_RETURN_SOURCE, "<go-union-nested-return>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2, target_language="go")
        body = east3.get("body", [])
        assert isinstance(body, list)
        as_chr_fn = body[1]
        assert isinstance(as_chr_fn, dict)
        fn_body = as_chr_fn.get("body", [])
        assert isinstance(fn_body, list)
        self.assertGreaterEqual(len(fn_body), 2)
        self.assertEqual(fn_body[0].get("kind"), "ErrorCheck")
        self.assertEqual(fn_body[1].get("kind"), "Return")

    def test_go_union_return_smoke_runs_for_nested_return_call(self) -> None:
        east2 = parse_python_source(NESTED_RETURN_SOURCE, "<go-union-nested-run>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2, target_language="go")
        meta = east3.setdefault("meta", {})
        assert isinstance(meta, dict)
        meta["emit_context"] = {"module_id": "app", "is_entry": True}
        go_code = emit_go_module(east3)
        env = dict(os.environ)
        env["PATH"] = "/home/node/.local/go/bin:" + env.get("PATH", "")
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "app.go").write_text(go_code, encoding="utf-8")
            (tmpdir / "py_runtime.go").write_text(
                (ROOT / "src" / "runtime" / "go" / "built_in" / "py_runtime.go").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (tmpdir / "pytra_built_in_error.go").write_text(_emit_builtin_error_go(), encoding="utf-8")
            build = subprocess.run(
                [
                    "go",
                    "build",
                    "-o",
                    str(tmpdir / "app"),
                    str(tmpdir / "py_runtime.go"),
                    str(tmpdir / "pytra_built_in_error.go"),
                    str(tmpdir / "app.go"),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(tmpdir / "app")], cwd=tmp, capture_output=True, text=True, env=env)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, "\x07\nbad\n")

    def test_go_union_return_fixture_lowers_error_nodes(self) -> None:
        east2 = parse_python_source(FIXTURE_SOURCE, "<go-union-fixture>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2, target_language="go")
        kinds = [str(node.get("kind", "")) for node in _walk(east3)]
        self.assertIn("ErrorReturn", kinds)
        self.assertIn("ErrorCheck", kinds)
        self.assertIn("ErrorCatch", kinds)

    def test_go_union_return_fixture_runs(self) -> None:
        east2 = parse_python_source(FIXTURE_SOURCE, "<go-union-fixture-run>").to_jv()
        resolve_east1_to_east2(east2, registry=_load_registry())
        east3 = lower_east2_to_east3(east2, target_language="go")
        meta = east3.setdefault("meta", {})
        assert isinstance(meta, dict)
        meta["emit_context"] = {"module_id": "app", "is_entry": True}
        go_code = emit_go_module(east3)
        env = dict(os.environ)
        env["PATH"] = "/home/node/.local/go/bin:" + env.get("PATH", "")
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "app.go").write_text(go_code, encoding="utf-8")
            (tmpdir / "py_runtime.go").write_text(
                (ROOT / "src" / "runtime" / "go" / "built_in" / "py_runtime.go").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (tmpdir / "pytra_built_in_error.go").write_text(_emit_builtin_error_go(), encoding="utf-8")
            build = subprocess.run(
                [
                    "go",
                    "build",
                    "-o",
                    str(tmpdir / "app"),
                    str(tmpdir / "py_runtime.go"),
                    str(tmpdir / "pytra_built_in_error.go"),
                    str(tmpdir / "app.go"),
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(tmpdir / "app")], cwd=tmp, capture_output=True, text=True, env=env)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, "7\nbad\n")


if __name__ == "__main__":
    unittest.main()
