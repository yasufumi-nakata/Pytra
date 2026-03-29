"""py2zig (EAST based) smoke tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT / "test" / "unit" / "backends") not in sys.path:
    sys.path.insert(0, str(ROOT / "test" / "unit" / "backends"))

from toolchain.emit.zig.emitter import load_zig_profile, transpile_to_zig, transpile_to_zig_native
from toolchain.misc.transpile_cli import load_east3_document


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
        target_lang="js",
    )
    return doc3 if isinstance(doc3, dict) else {}


def find_fixture_case(stem: str) -> Path:
    matches = sorted((ROOT / "test" / "fixtures").rglob(f"{stem}.py"))
    if not matches:
        raise FileNotFoundError(f"missing fixture: {stem}")
    return matches[0]


class Py2ZigSmokeTest(unittest.TestCase):
    def test_load_zig_profile_contains_core_sections(self) -> None:
        profile = load_zig_profile()
        self.assertIn("types", profile)
        self.assertIn("operators", profile)
        self.assertIn("syntax", profile)
        self.assertIn("runtime_calls", profile)

    def test_add_transpiles(self) -> None:
        fixture = find_fixture_case("add")
        east = load_east(fixture, parser_backend="self_hosted")
        zig_src = transpile_to_zig_native(east)
        self.assertTrue(zig_src.strip())
        self.assertIn("@import", zig_src)

    def test_if_else_transpiles(self) -> None:
        fixture = find_fixture_case("if_else")
        east = load_east(fixture, parser_backend="self_hosted")
        zig_src = transpile_to_zig_native(east)
        self.assertTrue(zig_src.strip())
        self.assertIn("if (", zig_src)

    def test_for_range_transpiles(self) -> None:
        fixture = find_fixture_case("for_range")
        east = load_east(fixture, parser_backend="self_hosted")
        zig_src = transpile_to_zig_native(east)
        self.assertTrue(zig_src.strip())
        self.assertIn("while (", zig_src)

    def test_fib_transpiles(self) -> None:
        fixture = find_fixture_case("fib")
        east = load_east(fixture, parser_backend="self_hosted")
        zig_src = transpile_to_zig_native(east)
        self.assertTrue(zig_src.strip())
        self.assertIn("fn ", zig_src)

    def test_class_transpiles(self) -> None:
        fixture = find_fixture_case("class")
        east = load_east(fixture, parser_backend="self_hosted")
        zig_src = transpile_to_zig_native(east)
        self.assertTrue(zig_src.strip())
        self.assertIn("struct", zig_src)

    def test_transpile_to_zig_compat_api(self) -> None:
        fixture = find_fixture_case("add")
        east = load_east(fixture, parser_backend="self_hosted")
        zig_src = transpile_to_zig(east)
        self.assertTrue(zig_src.strip())

    def test_invalid_east_stage_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            transpile_to_zig_native({"kind": "Module", "east_stage": 2, "body": []})

    def test_invalid_root_kind_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            transpile_to_zig_native({"kind": "NotModule", "east_stage": 3, "body": []})


if __name__ == "__main__":
    unittest.main()
