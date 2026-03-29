"""Unit tests for AnyAnnotationProhibitionPass."""

from __future__ import annotations

import unittest

from src.toolchain.misc.east_parts.east3_opt_passes.any_annotation_prohibition_pass import (
    AnyAnnotationProhibitionPass,
)
from src.toolchain.misc.east_parts.east3_optimizer import PassContext
from src.toolchain.misc.east_parts.east3_optimizer import PassResult


def _module(body: list[object]) -> dict[str, object]:
    return {"kind": "Module", "east_stage": 3, "meta": {}, "body": body}


def _fn(
    name: str,
    arg_types: dict[str, str],
    return_type: str,
    body: list[object] | None = None,
    *,
    lineno: int = 1,
) -> dict[str, object]:
    return {
        "kind": "FunctionDef",
        "name": name,
        "arg_types": arg_types,
        "return_type": return_type,
        "arg_order": list(arg_types.keys()),
        "body": body if body is not None else [],
        "source_span": {"lineno": lineno, "col": 0},
    }


def _ann_assign(
    var: str,
    annotation: str,
    *,
    lineno: int = 1,
) -> dict[str, object]:
    return {
        "kind": "AnnAssign",
        "target": {"kind": "Name", "id": var},
        "annotation": annotation,
        "source_span": {"lineno": lineno, "col": 0},
    }


_CTX = PassContext(opt_level=1)


class AnyAnnotationProhibitionPassTest(unittest.TestCase):
    def _run(self, body: list[object]) -> PassResult:
        return AnyAnnotationProhibitionPass().run(_module(body), _CTX)

    def _assert_no_violation(self, body: list[object]) -> None:
        result = self._run(body)
        self.assertFalse(result.changed)

    def _assert_violation(self, body: list[object], *, contains: str = "Any") -> None:
        with self.assertRaises(RuntimeError) as ctx:
            self._run(body)
        self.assertIn(contains, str(ctx.exception))

    # --- clean cases ---

    def test_concrete_param_type_passes(self) -> None:
        self._assert_no_violation([_fn("f", {"x": "int64"}, "str")])

    def test_union_type_passes(self) -> None:
        self._assert_no_violation([_fn("f", {"x": "str | int64"}, "bool")])

    def test_concrete_annassign_passes(self) -> None:
        self._assert_no_violation([_ann_assign("x", "list[str]")])

    def test_empty_body_passes(self) -> None:
        self._assert_no_violation([])

    def test_anylike_word_prefix_does_not_trigger(self) -> None:
        # "AnyFoo" should NOT be considered Any
        self._assert_no_violation([_fn("f", {"x": "AnyFoo"}, "AnyFoo")])

    # --- violation: function parameter ---

    def test_any_param_raises(self) -> None:
        self._assert_violation([_fn("f", {"x": "Any"}, "int64")])

    def test_any_nested_in_list_param_raises(self) -> None:
        self._assert_violation([_fn("f", {"x": "list[Any]"}, "int64")])

    def test_any_nested_in_dict_param_raises(self) -> None:
        self._assert_violation([_fn("f", {"x": "dict[str, Any]"}, "int64")])

    # --- violation: return type ---

    def test_any_return_type_raises(self) -> None:
        self._assert_violation([_fn("f", {"x": "int64"}, "Any")])

    def test_any_nested_return_raises(self) -> None:
        self._assert_violation([_fn("f", {}, "list[Any]")])

    # --- violation: AnnAssign ---

    def test_any_annassign_raises(self) -> None:
        self._assert_violation([_ann_assign("x", "Any")])

    def test_any_nested_in_annassign_raises(self) -> None:
        self._assert_violation([_ann_assign("m", "dict[str, Any]")])

    # --- violation: inside function body ---

    def test_any_annassign_in_function_body_raises(self) -> None:
        inner = _ann_assign("tmp", "Any", lineno=3)
        fn = _fn("g", {"y": "int64"}, "int64", body=[inner])
        self._assert_violation([fn])

    # --- violation: multiple violations reported together ---

    def test_multiple_violations_all_reported(self) -> None:
        fn1 = _fn("f", {"x": "Any"}, "str")
        fn2 = _fn("g", {}, "Any")
        with self.assertRaises(RuntimeError) as ctx:
            self._run([fn1, fn2])
        msg = str(ctx.exception)
        self.assertIn("parameter `x` of `f`", msg)
        self.assertIn("return type of `g`", msg)

    # --- error message quality ---

    def test_error_message_includes_hint(self) -> None:
        self._assert_violation(
            [_fn("f", {"x": "Any"}, "int64")],
            contains="concrete type",
        )

    def test_error_message_includes_variable_name(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            self._run([_ann_assign("my_var", "Any")])
        self.assertIn("my_var", str(ctx.exception))

    def test_error_message_includes_function_name(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            self._run([_fn("compute_result", {"x": "Any"}, "int64")])
        self.assertIn("compute_result", str(ctx.exception))

    # --- edge: nested class / if blocks ---

    def test_any_inside_class_body_raises(self) -> None:
        cls = {
            "kind": "ClassDef",
            "name": "MyClass",
            "body": [_fn("method", {"self": "MyClass", "v": "Any"}, "None")],
        }
        self._assert_violation([cls])

    def test_any_inside_if_body_raises(self) -> None:
        if_stmt = {
            "kind": "If",
            "test": {"kind": "Name", "id": "cond"},
            "body": [_ann_assign("x", "Any")],
            "orelse": [],
        }
        self._assert_violation([if_stmt])

    def test_clean_code_returns_unchanged_passresult(self) -> None:
        result = self._run([_fn("f", {"x": "str"}, "int64")])
        self.assertFalse(result.changed)
        self.assertEqual(result.change_count, 0)


if __name__ == "__main__":
    unittest.main()
