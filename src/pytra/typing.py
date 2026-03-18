"""Pytra typing module — re-exports from Python standard typing.

Python runtime: standard typing functions are available.
Transpiler: ignores this import (cast etc. are recognized natively).
"""

from typing import *  # noqa: F401,F403
