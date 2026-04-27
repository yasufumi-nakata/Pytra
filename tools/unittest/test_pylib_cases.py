from __future__ import annotations

import json
import shutil
import sys
import unittest
import typing as py_typing
from dataclasses import dataclass
from pathlib import Path, Path as StdPath
from typing import Any

try:
    import pytest
except ImportError:  # pragma: no cover - exercised in minimal local envs.
    pytest = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from src.pytra.std import argparse as py_argparse
from src.pytra.std import glob as py_glob
from src.pytra.std import json as py_json
from src.pytra.std import os as py_os
from src.pytra.std import re as py_re
from src.pytra.std import sys as py_sys
from src.pytra.enum import Enum, IntEnum, IntFlag
from src.pytra.std.pathlib import Path as PyPath


CASE_ROOT = ROOT / "test" / "cases" / "pylib"
WORK_ROOT = ROOT / "work" / "tmp" / "pylib-cases"
_MISSING = object()


@dataclass
class Point:
    x: int
    y: int = 0


@dataclass
class MyError(Exception):
    category: str
    summary: str


class Color(Enum):
    RED = 1
    BLUE = 2


class Status(IntEnum):
    OK = 0
    ERROR = 1


class Perm(IntFlag):
    READ = 1
    WRITE = 2
    EXEC = 4


def _case_paths() -> list[Path]:
    if not CASE_ROOT.exists():
        return []
    return sorted(CASE_ROOT.rglob("*.json"))


def _case_id(path: Path) -> str:
    return path.relative_to(CASE_ROOT).with_suffix("").as_posix()


def _load_case(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        case = json.load(f)
    if not isinstance(case, dict):
        raise AssertionError(f"{path}: case root must be an object")
    return case


def _run_named_case(name: str) -> dict[str, Any]:
    if name == "argparse_positional_option":
        p = py_argparse.ArgumentParser("x")
        p.add_argument("input")
        p.add_argument("-o", "--output")
        p.add_argument("--pretty", action="store_true")
        return p.parse_args(["a.py", "-o", "out.cpp", "--pretty"])
    if name == "argparse_choices":
        p = py_argparse.ArgumentParser("x")
        p.add_argument("input")
        p.add_argument("--mode", choices=["a", "b"], default="a")
        return p.parse_args(["in.py", "--mode", "b"])
    if name == "dataclasses_init_defaults":
        p = Point(1)
        return {"x": p.x, "y": p.y}
    if name == "dataclasses_repr_eq":
        a = Point(1, 2)
        b = Point(1, 2)
        c = Point(2, 1)
        return {"repr": repr(a), "a_eq_b": a == b, "a_eq_c": a == c}
    if name == "dataclasses_exception_subclass":
        e = MyError("kind", "message")
        return {"category": e.category, "summary": e.summary}
    if name == "enum_basic":
        return {"red_eq_red": Color.RED == Color.RED, "red_eq_blue": Color.RED == Color.BLUE}
    if name == "intenum_basic":
        return {"ok_eq_zero": Status.OK == 0, "error_int": int(Status.ERROR)}
    if name == "intflag_bitops":
        rw = Perm.READ | Perm.WRITE
        return {
            "rw": int(rw),
            "rw_and_write": int(rw & Perm.WRITE),
            "rw_xor_write": int(rw ^ Perm.WRITE),
        }
    if name == "re_match_basic":
        m = py_re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", "x = 1")
        if m is None:
            return {"group1": None, "group2": None}
        return {"group1": m.group(1), "group2": m.group(2)}
    if name == "re_sub_ws":
        return {"out": py_re.sub(r"\s+", " ", "a\nb\tc")}
    if name == "re_import_regex":
        return {
            "import_os_matches": py_re.match(r"^import\s+(.+)$", "import os") is not None,
            "import_modules_matches": py_re.match(
                r"^import\s+(.+)$", "import_modules: dict[str, str] = {}"
            )
            is not None,
        }
    if name == "sys_wrapper_exports":
        return {
            "argv_is_list": isinstance(py_sys.argv, list),
            "stderr_exists": py_sys.stderr is not None,
            "stdout_exists": py_sys.stdout is not None,
            "path_is_list": isinstance(py_sys.path, list),
        }
    if name == "sys_setters":
        old_argv = list(py_sys.argv)
        old_path = list(py_sys.path)
        try:
            py_sys.set_argv(["a", "b"])
            py_sys.set_path(["x"])
            return {"argv": list(py_sys.argv), "path": list(py_sys.path)}
        finally:
            py_sys.set_argv(old_argv)
            py_sys.set_path(old_path)
    if name == "typing_exports":
        values = [
            py_typing.Any,
            py_typing.List,
            py_typing.Set,
            py_typing.Dict,
            py_typing.Tuple,
            py_typing.Iterable,
            py_typing.Optional,
            py_typing.Union,
            py_typing.Callable,
        ]
        return {"all_present": all(v is not None for v in values)}
    if name == "typing_typevar_callable":
        t = py_typing.TypeVar("T")
        return {"typevar_exists": t is not None, "callable_exists": py_typing.Callable is not None}
    if name == "json_loads_basic_object":
        obj = py_json.loads_obj('{"a":1,"b":[true,false,null],"c":"x"}')
        assert obj is not None
        b = obj.get_arr("b")
        assert b is not None
        null_value = b.get(2)
        return {
            "is_obj": True,
            "a": obj.get_int("a"),
            "b0": b.get_bool(0),
            "b1": b.get_bool(1),
            "b2_is_null": null_value is not None and null_value.raw is None,
            "c": obj.get_str("c"),
        }
    if name == "json_loads_unicode_escape":
        obj = py_json.loads_obj('{"s":"\\u3042"}')
        assert obj is not None
        return {"s": obj.get_str("s")}
    if name == "json_loads_numbers_and_exponent":
        obj = py_json.loads_obj('{"i":-12,"f":3.25,"e":1.5e2,"ez":2E-1}')
        assert obj is not None
        return {
            "i": obj.get_int("i"),
            "f": obj.get_float("f"),
            "e": obj.get_float("e"),
            "ez": obj.get_float("ez"),
        }
    if name == "json_loads_string_escapes":
        obj = py_json.loads_obj('{"s":"a\\\\b\\n\\t\\\"\\/"}')
        assert obj is not None
        return {"s": obj.get_str("s")}
    if name == "json_loads_nested_roundtrip":
        src = {
            "name": "alpha",
            "ok": True,
            "none": None,
            "vals": [1, 2, {"x": "y", "z": [False, 3.5]}],
        }
        txt = py_json.dumps(src, ensure_ascii=False, separators=(",", ":"))
        return {"roundtrip": py_json.loads(txt).raw == src}
    if name == "json_loads_obj_decode_helpers":
        obj = py_json.loads_obj('{"name":"alpha","meta":{"ok":true},"vals":[1,2.5,false]}')
        assert obj is not None
        name_val = obj.get("name")
        meta = obj.get_obj("meta")
        vals = obj.get_arr("vals")
        assert name_val is not None and meta is not None and vals is not None
        return {
            "name": obj.get_str("name"),
            "name_as_str": name_val.as_str(),
            "meta_ok": meta.get_bool("ok"),
            "vals_0": vals.get_int(0),
            "vals_1": vals.get_float(1),
            "vals_2": vals.get_bool(2),
        }
    if name == "json_loads_arr_decode_helpers":
        arr = py_json.loads_arr('[{"ok":true}, ["x"], 5, "name", false]')
        assert arr is not None
        first_obj = arr.get_obj(0)
        nested = arr.get_arr(1)
        assert first_obj is not None and nested is not None
        return {
            "first_ok": first_obj.get_bool("ok"),
            "nested_0": nested.get_str(0),
            "int_2": arr.get_int(2),
            "str_3": arr.get_str(3),
            "bool_4": arr.get_bool(4),
        }
    if name == "json_loads_obj_rejects_shape_mismatch":
        return {
            "obj_is_none": py_json.loads_obj("[1,2,3]") is None,
            "arr_is_none": py_json.loads_arr('{"name":"alpha"}') is None,
        }
    if name == "json_loads_rejects_invalid_inputs":
        bad_cases = [
            "",
            "{",
            '{"a":1',
            '{"a",1}',
            '{"a":}',
            "[1,2,]",
            '{"a":tru}',
            '{"a":"\\x"}',
            '{"a":"\\u12G4"}',
            '{"a":1} trailing',
        ]
        rejected = 0
        for case in bad_cases:
            try:
                py_json.loads(case)
            except ValueError:
                rejected += 1
        return {"rejected": rejected, "total": len(bad_cases)}
    if name == "json_dumps_compact_and_pretty":
        obj = {"x": [1, 2], "y": "z"}
        compact = py_json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        pretty = py_json.dumps(obj, ensure_ascii=False, indent=2)
        return {
            "compact_has_x": '"x":[1,2]' in compact,
            "pretty_has_newline": "\n" in pretty,
            "pretty_has_indent": '  "x"' in pretty,
        }
    if name == "json_dumps_ensure_ascii":
        obj = {"s": "あ"}
        text_ascii = py_json.dumps(obj, ensure_ascii=True, separators=(",", ":"))
        text_utf8 = py_json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return {"ascii_has_escape": "\\u3042" in text_ascii, "utf8_has_char": "あ" in text_utf8}
    if name == "json_dumps_escapes_control_chars":
        out = py_json.dumps({"s": "\"\\\b\f\n\r\t"}, ensure_ascii=False, separators=(",", ":"))
        return {
            "quote": '\\"' in out,
            "backslash": "\\\\" in out,
            "backspace": "\\b" in out,
            "formfeed": "\\f" in out,
            "newline": "\\n" in out,
            "carriage": "\\r" in out,
            "tab": "\\t" in out,
        }
    if name == "json_dumps_rejects_unsupported_type":
        try:
            py_json.dumps({"x": {1, 2, 3}})
        except TypeError:
            return {"raises_type_error": True}
        return {"raises_type_error": False}
    if name == "path_basic_properties":
        p = PyPath("a/b/file.txt")
        return {"name": p.name, "stem": p.stem, "suffix": p.suffix, "parent": str(p.parent)}
    if name == "path_join_and_resolve":
        p = PyPath("a") / "b" / "c.txt"
        return {"path": str(p), "resolve_endswith": str(p.resolve()).endswith("a/b/c.txt")}
    if name == "path_text_io_and_exists":
        d = _fresh_work_dir("path_text_io_and_exists")
        p = PyPath(str(d)) / "x.txt"
        p.write_text("hello", encoding="utf-8")
        return {"exists": p.exists(), "text": p.read_text(encoding="utf-8")}
    if name == "path_mkdir_and_glob":
        d = PyPath(str(_fresh_work_dir("path_mkdir_and_glob"))) / "a" / "b"
        d.mkdir(parents=True, exist_ok=True)
        (d / "f1.txt").write_text("1")
        (d / "f2.py").write_text("2")
        return {"names": sorted(x.name for x in d.glob("*.txt"))}
    if name == "path_parents_index":
        p = PyPath("a/b/c/d.txt")
        return {"parent0": str(p.parents[0]), "parent1": str(p.parents[1])}
    if name == "os_path_subset":
        p = py_os.path.join("a", "b.txt")
        root, ext = py_os.path.splitext(p)
        return {"basename": py_os.path.basename(p), "root_ok": root.endswith("a/b") or root.endswith("a\\b"), "ext": ext}
    if name == "glob_basic":
        d = _fresh_work_dir("glob_basic")
        (d / "x.txt").write_text("x", encoding="utf-8")
        (d / "y.bin").write_text("y", encoding="utf-8")
        out = py_glob.glob(str(d / "*.txt"))
        return {"count": len(out), "first_endswith": len(out) == 1 and out[0].endswith("x.txt")}
    raise AssertionError(f"unknown pylib case: {name}")


def _fresh_work_dir(name: str) -> StdPath:
    path = WORK_ROOT / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_path(doc: Any, path_expr: str) -> Any:
    cur = doc
    for part in path_expr.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def _assert_case(path: Path, result: dict[str, Any], assertion: dict[str, Any]) -> None:
    path_expr = assertion.get("path")
    if not isinstance(path_expr, str):
        raise AssertionError(f"{path}: assertion path must be a string")
    actual = _get_path(result, path_expr)
    if "equals" in assertion:
        assert actual == assertion["equals"], f"{path}: {path_expr} = {actual!r}"
    if "exists" in assertion:
        expected = bool(assertion["exists"])
        assert (actual is not _MISSING) is expected, f"{path}: exists mismatch at {path_expr}"


def _run_pylib_case(path: Path) -> None:
    case = _load_case(path)
    name = case.get("case")
    if not isinstance(name, str):
        raise AssertionError(f"{path}: case must be a string")
    result = _run_named_case(name)
    assertions = case.get("assertions", [])
    if not isinstance(assertions, list):
        raise AssertionError(f"{path}: assertions must be a list")
    for assertion in assertions:
        if not isinstance(assertion, dict):
            raise AssertionError(f"{path}: assertion must be an object")
        _assert_case(path, result, assertion)


if pytest is not None:

    @pytest.mark.parametrize("path", _case_paths(), ids=_case_id)
    def test_pylib_case(path: Path) -> None:
        _run_pylib_case(path)

else:

    class PyLibCaseTests(unittest.TestCase):
        def test_pylib_cases(self) -> None:
            for path in _case_paths():
                with self.subTest(case=_case_id(path)):
                    _run_pylib_case(path)


if __name__ == "__main__":
    unittest.main()
