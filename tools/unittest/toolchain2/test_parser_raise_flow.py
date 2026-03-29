from __future__ import annotations

import unittest

from toolchain2.parse.py.parser import parse_python_source


BARE_RAISE_SOURCE = """
if __name__ == "__main__":
    try:
        raise ValueError("bad")
    except ValueError:
        raise
"""


RAISE_FROM_SOURCE = """
if __name__ == "__main__":
    try:
        raise ValueError("bad")
    except Exception as exc:
        raise RuntimeError("wrap: " + str(exc)) from exc
"""


class ParserRaiseFlowTests(unittest.TestCase):
    def test_parser_emits_raise_without_exc_for_bare_reraise(self) -> None:
        east1 = parse_python_source(BARE_RAISE_SOURCE, "<bare-raise>").to_jv()
        main_guard = east1.get("main_guard_body", [])
        self.assertIsInstance(main_guard, list)
        try_stmt = main_guard[0]
        handlers = try_stmt.get("handlers", [])
        inner_raise = handlers[0]["body"][0]
        self.assertEqual(inner_raise.get("kind"), "Raise")
        self.assertIsNone(inner_raise.get("exc"))
        self.assertIsNone(inner_raise.get("cause"))

    def test_parser_emits_raise_cause_for_raise_from(self) -> None:
        east1 = parse_python_source(RAISE_FROM_SOURCE, "<raise-from>").to_jv()
        main_guard = east1.get("main_guard_body", [])
        self.assertIsInstance(main_guard, list)
        try_stmt = main_guard[0]
        handlers = try_stmt.get("handlers", [])
        wrapped_raise = handlers[0]["body"][0]
        self.assertEqual(wrapped_raise.get("kind"), "Raise")
        exc = wrapped_raise.get("exc")
        cause = wrapped_raise.get("cause")
        self.assertIsInstance(exc, dict)
        self.assertIsInstance(cause, dict)
        self.assertEqual(cause.get("kind"), "Name")
        self.assertEqual(cause.get("id"), "exc")


if __name__ == "__main__":
    unittest.main()
