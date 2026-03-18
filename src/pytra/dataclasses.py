"""Pytra dataclasses module — re-exports from Python standard dataclasses.

Python runtime: standard dataclass/field are available.
Transpiler: ignores this import (dataclass decorator is recognized natively).
"""

from dataclasses import *  # noqa: F401,F403
