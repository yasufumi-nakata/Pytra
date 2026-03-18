"""Pytra enum module — re-exports from Python standard enum.

Python runtime: standard Enum/IntEnum/IntFlag are available.
Transpiler: ignores this import (enum classes are parsed natively).
"""

from enum import *  # noqa: F401,F403
