"""Tests for pytra.std.subprocess."""

from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "src")

from pytra.std.subprocess import CompletedProcess, run


class TestCompletedProcess(unittest.TestCase):
    def test_fields(self) -> None:
        cp = CompletedProcess(returncode=0, stdout="hello", stderr="")
        self.assertEqual(cp.returncode, 0)
        self.assertEqual(cp.stdout, "hello")
        self.assertEqual(cp.stderr, "")

    def test_nonzero_returncode(self) -> None:
        cp = CompletedProcess(returncode=42, stdout="", stderr="err")
        self.assertEqual(cp.returncode, 42)
        self.assertEqual(cp.stderr, "err")


class TestRun(unittest.TestCase):
    def test_echo(self) -> None:
        result = run(["echo", "hello"], capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "hello")
        self.assertEqual(result.stderr, "")

    def test_false_returns_nonzero(self) -> None:
        result = run(["false"])
        self.assertNotEqual(result.returncode, 0)

    def test_true_returns_zero(self) -> None:
        result = run(["true"])
        self.assertEqual(result.returncode, 0)

    def test_capture_stderr(self) -> None:
        result = run(
            [sys.executable, "-c", "import sys; sys.stderr.write('warn\\n')"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("warn", result.stderr)

    def test_cwd(self) -> None:
        result = run(["pwd"], cwd="/tmp", capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("/tmp", result.stdout.strip())

    def test_env(self) -> None:
        result = run(
            [sys.executable, "-c", "import os; print(os.environ.get('PYTRA_TEST_VAR', ''))"],
            capture_output=True,
            env={"PYTRA_TEST_VAR": "hello_from_test"},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "hello_from_test")

    def test_env_does_not_clobber_path(self) -> None:
        """Setting env should merge with parent env, not replace it."""
        result = run(
            [sys.executable, "-c", "import os; print(os.environ.get('PATH', ''))"],
            capture_output=True,
            env={"PYTRA_TEST_EXTRA": "1"},
        )
        self.assertEqual(result.returncode, 0)
        # PATH should still be present (inherited from parent)
        self.assertNotEqual(result.stdout.strip(), "")

    def test_no_capture(self) -> None:
        result = run(["echo", "quiet"])
        self.assertEqual(result.returncode, 0)
        # stdout/stderr should be empty strings when not captured
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
