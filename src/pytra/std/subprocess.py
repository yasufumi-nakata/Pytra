"""pytra.std.subprocess: subprocess API with Python runtime fallback.

Provides a minimal subprocess.run() that works in both Python host and
C++ selfhost (via std::system / posix_spawn).
"""

import subprocess as _subprocess

from pytra.std import extern


class CompletedProcess:
    """Result of a subprocess run."""

    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode: int = returncode
        self.stdout: str = stdout
        self.stderr: str = stderr


@extern
def run(cmd: list[str], cwd: str = "", capture_output: bool = False, env: dict[str, str] = {}) -> CompletedProcess:
    """Run a command as a subprocess.

    Args:
        cmd: Command and arguments.
        cwd: Working directory (empty string = inherit).
        capture_output: If True, capture stdout/stderr as strings.
        env: Environment variables. Empty dict = inherit parent env.

    Returns:
        CompletedProcess with returncode and optional stdout/stderr.
    """
    import os as _os
    kwargs: dict[str, object] = {}
    if cwd != "":
        kwargs["cwd"] = cwd
    if capture_output:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    if len(env) > 0:
        merged = dict(_os.environ)
        for k, v in env.items():
            merged[k] = v
        kwargs["env"] = merged
    proc = _subprocess.run(cmd, **kwargs)
    stdout_txt = ""
    stderr_txt = ""
    if capture_output:
        if isinstance(proc.stdout, str):
            stdout_txt = proc.stdout
        if isinstance(proc.stderr, str):
            stderr_txt = proc.stderr
    return CompletedProcess(proc.returncode, stdout_txt, stderr_txt)
