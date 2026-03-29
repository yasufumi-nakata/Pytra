"""Tests for EAST3 swap pattern detection (Name-only Swap contract)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from src.toolchain.compile.east2_to_east3_swap_detection import (
    detect_swap_patterns,
    _swap_tmp_counter,
)


def _name(ident: str) -> dict:
    return {"kind": "Name", "id": ident}


def _subscript(owner: str, index: str) -> dict:
    return {"kind": "Subscript", "value": _name(owner), "slice": _name(index)}


def _subscript_binop(owner: str, index: str, op: str, rhs_val: int) -> dict:
    return {
        "kind": "Subscript",
        "value": _name(owner),
        "slice": {
            "kind": "BinOp",
            "left": _name(index),
            "op": op,
            "right": {"kind": "Constant", "value": rhs_val},
        },
    }


def _tuple_assign(left_elems: list, right_elems: list) -> dict:
    return {
        "kind": "Assign",
        "source_span": {"lineno": 1, "col": 0},
        "target": {"kind": "Tuple", "elements": left_elems},
        "value": {"kind": "Tuple", "elements": right_elems},
    }


def _wrap_in_module(stmts: list) -> dict:
    return {
        "kind": "Module",
        "body": [{"kind": "FunctionDef", "name": "f", "body": stmts}],
    }


class SwapDetectionTest(unittest.TestCase):
    def setUp(self) -> None:
        _swap_tmp_counter[0] = 0

    def test_name_name_swap_becomes_swap_node(self) -> None:
        """a, b = b, a → Swap node with Name left/right."""
        module = _wrap_in_module([
            _tuple_assign([_name("a"), _name("b")], [_name("b"), _name("a")]),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["kind"], "Swap")
        self.assertEqual(body[0]["left"]["id"], "a")
        self.assertEqual(body[0]["right"]["id"], "b")

    def test_subscript_swap_expands_to_assign_sequence(self) -> None:
        """values[i], values[j] = values[j], values[i] → 3 Assign statements."""
        module = _wrap_in_module([
            _tuple_assign(
                [_subscript("values", "i"), _subscript("values", "j")],
                [_subscript("values", "j"), _subscript("values", "i")],
            ),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        self.assertEqual(len(body), 3)
        # Statement 1: tmp = values[i]
        self.assertEqual(body[0]["kind"], "Assign")
        self.assertEqual(body[0]["target"]["kind"], "Name")
        self.assertEqual(body[0]["target"]["id"], "__swap_tmp_0")
        self.assertEqual(body[0]["value"]["kind"], "Subscript")
        # Statement 2: values[i] = values[j]
        self.assertEqual(body[1]["kind"], "Assign")
        self.assertEqual(body[1]["target"]["kind"], "Subscript")
        self.assertEqual(body[1]["value"]["kind"], "Subscript")
        # Statement 3: values[j] = tmp
        self.assertEqual(body[2]["kind"], "Assign")
        self.assertEqual(body[2]["target"]["kind"], "Subscript")
        self.assertEqual(body[2]["value"]["kind"], "Name")
        self.assertEqual(body[2]["value"]["id"], "__swap_tmp_0")

    def test_subscript_binop_swap_expands(self) -> None:
        """values[j], values[j+1] = values[j+1], values[j] → 3 Assign statements.

        This is the bubble sort pattern from sample/py/12_sort_visualizer.py.
        """
        module = _wrap_in_module([
            _tuple_assign(
                [_subscript("values", "j"), _subscript_binop("values", "j", "Add", 1)],
                [_subscript_binop("values", "j", "Add", 1), _subscript("values", "j")],
            ),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        self.assertEqual(len(body), 3)
        self.assertEqual(body[0]["kind"], "Assign")
        self.assertEqual(body[0]["target"]["id"], "__swap_tmp_0")
        self.assertEqual(body[2]["value"]["id"], "__swap_tmp_0")

    def test_no_swap_node_for_subscript(self) -> None:
        """Subscript swaps must never produce a Swap node."""
        module = _wrap_in_module([
            _tuple_assign(
                [_subscript("a", "i"), _subscript("a", "j")],
                [_subscript("a", "j"), _subscript("a", "i")],
            ),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        for stmt in body:
            self.assertNotEqual(stmt.get("kind"), "Swap")

    def test_mixed_name_subscript_swap_expands(self) -> None:
        """a, xs[i] = xs[i], a → Assign expansion (not Swap)."""
        module = _wrap_in_module([
            _tuple_assign(
                [_name("a"), _subscript("xs", "i")],
                [_subscript("xs", "i"), _name("a")],
            ),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        self.assertEqual(len(body), 3)
        for stmt in body:
            self.assertNotEqual(stmt.get("kind"), "Swap")

    def test_non_swap_tuple_assign_unchanged(self) -> None:
        """a, b = c, d (not a swap) → left as-is."""
        module = _wrap_in_module([
            _tuple_assign([_name("a"), _name("b")], [_name("c"), _name("d")]),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["kind"], "Assign")

    def test_multiple_swaps_get_unique_tmp_names(self) -> None:
        """Two Subscript swaps get different tmp variable names."""
        module = _wrap_in_module([
            _tuple_assign(
                [_subscript("a", "i"), _subscript("a", "j")],
                [_subscript("a", "j"), _subscript("a", "i")],
            ),
            _tuple_assign(
                [_subscript("b", "x"), _subscript("b", "y")],
                [_subscript("b", "y"), _subscript("b", "x")],
            ),
        ])
        detect_swap_patterns(module)
        body = module["body"][0]["body"]
        self.assertEqual(len(body), 6)
        self.assertEqual(body[0]["target"]["id"], "__swap_tmp_0")
        self.assertEqual(body[3]["target"]["id"], "__swap_tmp_1")


if __name__ == "__main__":
    unittest.main()
