from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
import os
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


def _run_go(source: str, *, type_info_table: dict[str, object] | None = None) -> str:
    run = _run_go_process(source, type_info_table=type_info_table)
    if run.returncode != 0:
        raise AssertionError(f"{run.stdout}\n{run.stderr}")
    return run.stdout


def _run_go_process(
    source: str,
    *,
    type_info_table: dict[str, object] | None = None,
) -> subprocess.CompletedProcess[str]:
    east2 = parse_python_source(source, "<go-exception-smoke>").to_jv()
    resolve_east1_to_east2(east2, registry=_load_registry())
    # Broad exception smokes stay on the existing Go emitter Raise/Try path.
    # union_return-specific coverage lives in test_go_union_return_lowering.py.
    east3 = lower_east2_to_east3(east2, target_language="core")
    meta = east3.setdefault("meta", {})
    assert isinstance(meta, dict)
    meta["emit_context"] = {"module_id": "app", "is_entry": True}
    if type_info_table is not None:
        meta["linked_program_v1"] = {"type_info_table_v1": type_info_table}
    go_code = emit_go_module(east3)

    with tempfile.TemporaryDirectory() as tmp:
        go_path = Path(tmp) / "app.go"
        runtime_path = ROOT / "src" / "runtime" / "go" / "built_in" / "py_runtime.go"
        bundled_runtime = Path(tmp) / "py_runtime.go"
        bundled_errors = Path(tmp) / "pytra_built_in_error.go"
        bundled_type_ids = Path(tmp) / "pytra_type_id_table.go"
        out_path = Path(tmp) / "app"
        env = dict(os.environ)
        env["PATH"] = "/home/node/.local/go/bin:" + env.get("PATH", "")
        go_path.write_text(go_code, encoding="utf-8")
        bundled_runtime.write_text(runtime_path.read_text(encoding="utf-8"), encoding="utf-8")
        bundled_errors.write_text(_emit_builtin_error_go(), encoding="utf-8")
        helper_type_info: dict[str, object] = {
            "object": {"id": 8, "entry": 8, "exit": 16},
            "BaseException": {"id": 9, "entry": 9, "exit": 16},
            "Exception": {"id": 10, "entry": 10, "exit": 16},
            "RuntimeError": {"id": 11, "entry": 11, "exit": 12},
            "ValueError": {"id": 12, "entry": 12, "exit": 13},
            "TypeError": {"id": 13, "entry": 13, "exit": 14},
            "IndexError": {"id": 14, "entry": 14, "exit": 15},
            "KeyError": {"id": 15, "entry": 15, "exit": 16},
        }
        bundled_type_ids.write_text(_go_type_id_table_source(helper_type_info), encoding="utf-8")
        build = subprocess.run(
            ["go", "build", "-o", str(out_path), str(bundled_runtime), str(bundled_errors), str(bundled_type_ids), str(go_path)],
            cwd=tmp,
            capture_output=True,
            text=True,
            env=env,
        )
        if build.returncode != 0:
            raise AssertionError(f"{build.stdout}\n{build.stderr}")
        run = subprocess.run([str(out_path)], cwd=tmp, capture_output=True, text=True, env=env)

    return run


def _go_type_id_table_source(type_info_table: dict[str, object]) -> str:
    rows: list[tuple[str, dict[str, int]]] = []
    for fqcn, info in type_info_table.items():
        if not isinstance(fqcn, str) or not isinstance(info, dict):
            continue
        id_val = info.get("id")
        entry = info.get("entry")
        exit_val = info.get("exit")
        if isinstance(id_val, int) and isinstance(entry, int) and isinstance(exit_val, int):
            rows.append((fqcn, {"id": id_val, "entry": entry, "exit": exit_val}))
    rows.sort(key=lambda item: item[1]["id"])

    table_values: list[str] = []
    const_rows: list[str] = []
    tid = 0
    for fqcn, info in rows:
        table_values.append(str(info["entry"]))
        table_values.append(str(info["exit"] - 1))
        name = fqcn
        snake: list[str] = []
        prev_lower = False
        for ch in name:
            if ch == ".":
                snake.append("_")
                prev_lower = False
                continue
            is_upper = "A" <= ch and ch <= "Z"
            is_lower = "a" <= ch and ch <= "z"
            if is_upper and prev_lower:
                snake.append("_")
            snake.append(ch.upper())
            prev_lower = is_lower
        const_rows.append("var " + "".join(snake) + "_TID int64 = " + str(tid))
        tid += 1

    lines = [
        "package main",
        "",
        "var id_table *PyList[int64] = PyListFromSlice[int64]([]int64{" + ", ".join(table_values) + "})",
        "",
    ]
    lines.extend(const_rows)
    lines.append("")
    return "\n".join(lines)


SOURCE = """
def parse(flag: bool) -> int:
    if flag:
        raise ValueError("bad")
    return 7

if __name__ == "__main__":
    try:
        print(parse(False))
        print(parse(True))
    except ValueError as e:
        print(e)
    finally:
        print("done")
"""

MULTI_HANDLER_SOURCE = """
if __name__ == "__main__":
    try:
        raise IndexError("idx")
    except ValueError as e:
        print("value", e)
    except IndexError as e:
        print("index", e)
    finally:
        print("done")
"""

FINALLY_ONLY_SOURCE = """
if __name__ == "__main__":
    try:
        raise ValueError("boom")
    finally:
        print("cleanup")
"""

CUSTOM_EXCEPTION_SOURCE = """
class ParseError(ValueError):
    pass

if __name__ == "__main__":
    try:
        raise ParseError("bad parse")
    except ParseError as e:
        print(e)
"""

CUSTOM_EXCEPTION_BASE_CATCH_SOURCE = """
class ParseError(ValueError):
    pass

if __name__ == "__main__":
    try:
        raise ParseError("bad parse")
    except ValueError as e:
        print("value", e)
"""

CUSTOM_EXCEPTION_INIT_SOURCE = """
class ParseError(ValueError):
    def __init__(self, msg: str):
        self.detail = msg

if __name__ == "__main__":
    try:
        raise ParseError("bad parse")
    except ValueError as e:
        print(e)
"""

CUSTOM_EXCEPTION_RERAISE_SOURCE = """
class ParseError(ValueError):
    pass

if __name__ == "__main__":
    err = ParseError("bad parse")
    try:
        raise err
    except ValueError as e:
        print(e)
"""

CUSTOM_EXCEPTION_CUSTOM_BASE_SOURCE = """
class ParseBase(Exception):
    pass

class ParseError(ParseBase):
    pass

if __name__ == "__main__":
    try:
        raise ParseError("bad parse")
    except ParseBase as e:
        print(e)
"""

WRAPPED_EXCEPTION_SOURCE = """
if __name__ == "__main__":
    try:
        try:
            raise ValueError("bad")
        except Exception as exc:
            raise RuntimeError("wrap: " + str(exc))
    except RuntimeError as err:
        print(err)
"""

WRAPPED_EXCEPTION_FROM_SOURCE = """
if __name__ == "__main__":
    try:
        try:
            raise ValueError("bad")
        except Exception as exc:
            raise RuntimeError("wrap: " + str(exc)) from exc
    except RuntimeError as err:
        print(err)
"""

BARE_RERAISE_SOURCE = """
if __name__ == "__main__":
    try:
        try:
            raise ValueError("bad")
        except ValueError:
            raise
    except ValueError as err:
        print(err)
"""

PROPAGATION_TWO_FRAMES_SOURCE = (
    FIXTURE_ROOT / "control" / "exception_propagation_two_frames.py"
).read_text(encoding="utf-8")
PROPAGATION_RAISE_FROM_SOURCE = (
    FIXTURE_ROOT / "control" / "exception_propagation_raise_from.py"
).read_text(encoding="utf-8")
BARE_RERAISE_FIXTURE_SOURCE = (
    FIXTURE_ROOT / "control" / "exception_bare_reraise.py"
).read_text(encoding="utf-8")
FINALLY_ORDER_FIXTURE_SOURCE = (
    FIXTURE_ROOT / "control" / "exception_finally_order.py"
).read_text(encoding="utf-8")


class GoExceptionSmokeTests(unittest.TestCase):
    def test_registry_loads_builtin_error_classes(self) -> None:
        reg = _load_registry()
        cls = reg.find_stdlib_class("ValueError")
        self.assertIsNotNone(cls)
        assert cls is not None
        self.assertEqual(cls.name, "ValueError")

    def test_go_emits_typed_value_error_catch_and_finally(self) -> None:
        stdout = _run_go(SOURCE)
        self.assertEqual(stdout, "7\nbad\ndone\n")

    def test_go_emits_multiple_exception_handlers(self) -> None:
        stdout = _run_go(MULTI_HANDLER_SOURCE)
        self.assertEqual(stdout, "index idx\ndone\n")

    def test_go_finally_runs_before_unhandled_rethrow(self) -> None:
        run = _run_go_process(FINALLY_ONLY_SOURCE)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout, "cleanup\n")
        self.assertIn("boom", run.stderr)

    def test_go_emits_exact_custom_exception_catch(self) -> None:
        stdout = _run_go(
            CUSTOM_EXCEPTION_SOURCE,
            type_info_table={
                "app.ParseError": {"id": 1000, "entry": 1000, "exit": 1001},
            },
        )
        self.assertEqual(stdout, "bad parse\n")

    def test_go_builtin_base_handler_catches_custom_descendant(self) -> None:
        stdout = _run_go(
            CUSTOM_EXCEPTION_BASE_CATCH_SOURCE,
            type_info_table={
                "app.ParseError": {"id": 1000, "entry": 1000, "exit": 1001},
            },
        )
        self.assertEqual(stdout, "value bad parse\n")

    def test_go_custom_exception_init_preserves_message(self) -> None:
        stdout = _run_go(
            CUSTOM_EXCEPTION_INIT_SOURCE,
            type_info_table={
                "app.ParseError": {"id": 1000, "entry": 1000, "exit": 1001},
            },
        )
        self.assertEqual(stdout, "bad parse\n")

    def test_go_reraise_custom_exception_instance(self) -> None:
        stdout = _run_go(
            CUSTOM_EXCEPTION_RERAISE_SOURCE,
            type_info_table={
                "app.ParseError": {"id": 1000, "entry": 1000, "exit": 1001},
            },
        )
        self.assertEqual(stdout, "bad parse\n")

    def test_go_custom_base_handler_catches_custom_descendant(self) -> None:
        stdout = _run_go(
            CUSTOM_EXCEPTION_CUSTOM_BASE_SOURCE,
            type_info_table={
                "app.ParseBase": {"id": 1000, "entry": 1000, "exit": 1002},
                "app.ParseError": {"id": 1001, "entry": 1001, "exit": 1002},
            },
        )
        self.assertEqual(stdout, "bad parse\n")

    def test_go_preserves_wrapped_exception_pattern(self) -> None:
        stdout = _run_go(WRAPPED_EXCEPTION_SOURCE)
        self.assertEqual(stdout, "wrap: bad\n")

    def test_go_parses_and_emits_raise_from_pattern(self) -> None:
        stdout = _run_go(WRAPPED_EXCEPTION_FROM_SOURCE)
        self.assertEqual(stdout, "wrap: bad\n")

    def test_go_bare_raise_rethrows_current_exception(self) -> None:
        stdout = _run_go(BARE_RERAISE_SOURCE)
        self.assertEqual(stdout, "bad\n")

    def test_go_propagates_exception_two_frames_up(self) -> None:
        stdout = _run_go(PROPAGATION_TWO_FRAMES_SOURCE)
        self.assertEqual(stdout, "caught boom\n")

    def test_go_propagates_raise_from_two_frames_up(self) -> None:
        stdout = _run_go(PROPAGATION_RAISE_FROM_SOURCE)
        self.assertEqual(stdout, "wrapped\n")

    def test_go_bare_raise_fixture_rethrows_current_exception(self) -> None:
        stdout = _run_go(BARE_RERAISE_FIXTURE_SOURCE)
        self.assertEqual(stdout, "boom\n")

    def test_go_finally_fixture_runs_before_outer_catch(self) -> None:
        run = _run_go_process(FINALLY_ORDER_FIXTURE_SOURCE)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(run.stdout, "cleanup\ncaught\n")


if __name__ == "__main__":
    unittest.main()
