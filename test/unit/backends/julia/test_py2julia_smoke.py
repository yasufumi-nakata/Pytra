"""py2julia (EAST based) smoke tests — transpile + output parity."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from toolchain.emit.julia.emitter import transpile_to_julia, transpile_to_julia_native
from toolchain.misc.transpile_cli import load_east3_document

RUNTIME_SRC = ROOT / "src" / "runtime" / "julia" / "built_in" / "py_runtime.jl"
JULIA_BIN = shutil.which("julia") or ""
PYTHON_BIN = sys.executable or "python3"


def load_east(
    input_path: Path,
    parser_backend: str = "self_hosted",
    east_stage: str = "3",
    object_dispatch_mode: str = "native",
    east3_opt_level: str = "1",
    east3_opt_pass: str = "",
    dump_east3_before_opt: str = "",
    dump_east3_after_opt: str = "",
    dump_east3_opt_trace: str = "",
):
    if east_stage != "3":
        raise RuntimeError("unsupported east_stage: " + east_stage)
    doc3 = load_east3_document(
        input_path,
        parser_backend=parser_backend,
        object_dispatch_mode=object_dispatch_mode,
        east3_opt_level=east3_opt_level,
        east3_opt_pass=east3_opt_pass,
        dump_east3_before_opt=dump_east3_before_opt,
        dump_east3_after_opt=dump_east3_after_opt,
        dump_east3_opt_trace=dump_east3_opt_trace,
        target_lang="julia",
    )
    return doc3 if isinstance(doc3, dict) else {}


def find_fixture_case(stem: str) -> Path:
    matches = sorted((ROOT / "test" / "fixtures").rglob(f"{stem}.py"))
    if not matches:
        raise FileNotFoundError(f"missing fixture: {stem}")
    return matches[0]


def _run_python(fixture_path: Path, timeout: int = 15) -> str:
    """Run a Python fixture and return its stdout."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    cp = subprocess.run(
        [PYTHON_BIN, str(fixture_path)],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    if cp.returncode != 0:
        raise RuntimeError(f"Python fixture failed: {cp.stderr[:300]}")
    return cp.stdout


def _run_julia(source: str, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    """Write source to a temp dir with runtime and run julia."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = Path(tmpdir) / "main.jl"
        src_path.write_text(source, encoding="utf-8")
        shutil.copy2(str(RUNTIME_SRC), str(Path(tmpdir) / "py_runtime.jl"))
        return subprocess.run(
            [JULIA_BIN, str(src_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )


def _normalize_output(text: str) -> str:
    """Normalize output for comparison: strip trailing whitespace per line."""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines)


# ── Transpile-only tests ──


class Py2JuliaSmokeTest(unittest.TestCase):
    def test_julia_runtime_exists(self) -> None:
        self.assertTrue(RUNTIME_SRC.exists())

    def test_transpile_simple_add(self) -> None:
        east_doc = load_east(find_fixture_case("add"))
        source = transpile_to_julia_native(east_doc)
        self.assertIsInstance(source, str)
        self.assertIn("function", source)
        self.assertIn("end", source)

    def test_transpile_fib(self) -> None:
        east_doc = load_east(find_fixture_case("fib"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("function", source)
        self.assertIn("if", source)

    def test_transpile_if_else(self) -> None:
        east_doc = load_east(find_fixture_case("if_else"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("if", source)
        self.assertIn("end", source)

    def test_transpile_for_loop(self) -> None:
        east_doc = load_east(find_fixture_case("for_range"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("for", source)
        self.assertIn("end", source)

    def test_transpile_loop(self) -> None:
        east_doc = load_east(find_fixture_case("loop"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("for", source)
        self.assertIn("end", source)

    def test_transpile_compare(self) -> None:
        east_doc = load_east(find_fixture_case("compare"))
        source = transpile_to_julia_native(east_doc)
        self.assertIsInstance(source, str)

    def test_transpile_dict_literal_entries(self) -> None:
        east_doc = load_east(find_fixture_case("dict_literal_entries"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("Dict", source)

    def test_transpile_class(self) -> None:
        east_doc = load_east(find_fixture_case("class_body_pass"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("mutable struct", source)
        self.assertIn("end", source)

    def test_transpile_assign(self) -> None:
        east_doc = load_east(find_fixture_case("assign"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("=", source)

    def test_transpile_to_julia_api_compat(self) -> None:
        """transpile_to_julia is an alias for transpile_to_julia_native."""
        east_doc = load_east(find_fixture_case("add"))
        source = transpile_to_julia(east_doc)
        self.assertIsInstance(source, str)
        self.assertIn("function", source)


# ── Output parity tests (require julia binary) ──


@unittest.skipUnless(JULIA_BIN, "julia not found in PATH")
class Py2JuliaParityTest(unittest.TestCase):
    """Transpile fixtures to Julia, run both Python and Julia, compare output."""

    def _assert_parity(self, fixture_stem: str) -> None:
        fixture_path = find_fixture_case(fixture_stem)

        # Python execution
        py_out = _run_python(fixture_path)

        # Julia execution
        east_doc = load_east(fixture_path)
        source = transpile_to_julia_native(east_doc)
        jl_cp = _run_julia(source)
        self.assertEqual(
            jl_cp.returncode, 0,
            f"{fixture_stem}: julia exited {jl_cp.returncode}\nstderr: {jl_cp.stderr[:500]}",
        )

        # Compare output
        py_norm = _normalize_output(py_out)
        jl_norm = _normalize_output(jl_cp.stdout)
        self.assertEqual(
            py_norm, jl_norm,
            f"{fixture_stem}: output parity mismatch\n"
            f"--- Python ---\n{py_norm}\n"
            f"--- Julia ---\n{jl_norm}",
        )

    # core
    def test_parity_add(self) -> None:
        self._assert_parity("add")

    def test_parity_fib(self) -> None:
        self._assert_parity("fib")

    def test_parity_assign(self) -> None:
        self._assert_parity("assign")

    def test_parity_compare(self) -> None:
        self._assert_parity("compare")

    def test_parity_float(self) -> None:
        self._assert_parity("float")

    def test_parity_dict_literal_entries(self) -> None:
        self._assert_parity("dict_literal_entries")

    def test_parity_lambda_as_arg(self) -> None:
        self._assert_parity("lambda_as_arg")

    def test_parity_lambda_immediate(self) -> None:
        self._assert_parity("lambda_immediate")

    # control flow
    def test_parity_if_else(self) -> None:
        self._assert_parity("if_else")

    def test_parity_for_range(self) -> None:
        self._assert_parity("for_range")

    def test_parity_loop(self) -> None:
        self._assert_parity("loop")

    def test_parity_not(self) -> None:
        self._assert_parity("not")

    def test_parity_ifexp_bool(self) -> None:
        self._assert_parity("ifexp_bool")

    def test_parity_try_raise(self) -> None:
        self._assert_parity("try_raise")

    def test_parity_finally(self) -> None:
        self._assert_parity("finally")

    # collections
    def test_parity_comprehension(self) -> None:
        self._assert_parity("comprehension")

    def test_parity_comprehension_filter(self) -> None:
        self._assert_parity("comprehension_filter")

    def test_parity_in_membership(self) -> None:
        self._assert_parity("in_membership")

    def test_parity_negative_index(self) -> None:
        self._assert_parity("negative_index")

    def test_parity_slice_basic(self) -> None:
        self._assert_parity("slice_basic")

    @unittest.skip("dict_get_items: items() on object receiver forbidden by parser constraint")
    def test_parity_dict_get_items(self) -> None:
        self._assert_parity("dict_get_items")

    def test_parity_dict_in(self) -> None:
        self._assert_parity("dict_in")

    def test_parity_list_repeat(self) -> None:
        self._assert_parity("list_repeat")

    # strings
    def test_parity_string(self) -> None:
        self._assert_parity("string")

    def test_parity_string_ops(self) -> None:
        self._assert_parity("string_ops")

    # classes
    def test_parity_class_body_pass(self) -> None:
        self._assert_parity("class_body_pass")

    def test_parity_class_instance(self) -> None:
        self._assert_parity("class_instance")

    def test_parity_class_member(self) -> None:
        self._assert_parity("class_member")


if __name__ == "__main__":
    unittest.main()
