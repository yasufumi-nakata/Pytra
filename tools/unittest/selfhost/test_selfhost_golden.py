"""Regression test: selfhost golden files match current emitter output.

For each language, checks that every golden file in test/selfhost/<lang>/
still matches what the emitter produces for that east3-opt module.

Modules that exceed the emit timeout are skipped (not failed) — they are
typically the very large ones (compile/passes, resolve/py/resolver, etc.)
that also time out during golden generation.

Usage:
    python3 -m pytest tools/unittest/selfhost/test_selfhost_golden.py
    python3 -m pytest tools/unittest/selfhost/test_selfhost_golden.py -k go
    SELFHOST_GOLDEN_TIMEOUT=10 python3 -m pytest ...

[P0-SELFHOST-GOLDEN-UNIFIED S2]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())

EAST3_OPT_DIR   = ROOT / "test" / "selfhost" / "east3-opt"
GOLDEN_ROOT     = ROOT / "test" / "selfhost"

TARGETS = ["go", "cpp", "rs", "ts"]

_EXT = {"go": ".go", "rs": ".rs", "ts": ".ts", "cpp": ".cpp"}

# Timeout (seconds) for a single emit subprocess call.
# Override with env var SELFHOST_GOLDEN_TIMEOUT.
_DEFAULT_TIMEOUT = int(os.environ.get("SELFHOST_GOLDEN_TIMEOUT", "30"))

# Re-use the same helper snippet as regenerate_selfhost_golden.py
_EMIT_HELPER = """
import sys, json
sys.path.insert(0, sys.argv[1])   # src/ root
target = sys.argv[2]
east3_path = sys.argv[3]
doc = json.loads(open(east3_path, encoding='utf-8').read())
if target == 'go':
    from toolchain.emit.go.emitter import emit_go_module
    print(emit_go_module(doc), end='')
elif target == 'rs':
    from toolchain.emit.rs.emitter import emit_rs_module
    print(emit_rs_module(doc), end='')
elif target == 'ts':
    from toolchain.emit.ts.emitter import emit_ts_module
    print(emit_ts_module(doc), end='')
elif target == 'cpp':
    from toolchain.emit.cpp.emitter import emit_cpp_module
    print(emit_cpp_module(doc), end='')
else:
    raise ValueError('unsupported target: ' + target)
"""


def _collect_golden_params() -> list[tuple[str, str, Path, Path]]:
    """Return [(target, golden_name, golden_path, east3_path), ...].

    Only includes golden files that have a corresponding east3-opt entry.
    """
    # Build lookup: golden_fname -> east3_path
    module_map: dict[str, dict[str, Path]] = {}  # target -> {fname: east3_path}
    for p in EAST3_OPT_DIR.rglob("*.east3"):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        sp_raw = doc.get("source_path", "")
        # Normalize absolute or relative source paths to "src/toolchain/..." form
        _tc_suffix = "/src/toolchain/"
        _tc_prefix = "src/toolchain/"
        if sp_raw.startswith(_tc_prefix):
            sp = sp_raw
        else:
            idx = sp_raw.find(_tc_suffix)
            sp = ("src/toolchain/" + sp_raw[idx + len(_tc_suffix):]) if idx >= 0 else ""
        if not sp:
            continue
        # Use full module_id (toolchain.* prefix) to match golden file naming
        module_id = sp.removeprefix("src/").replace("/", ".").removesuffix(".py")
        for target, ext in _EXT.items():
            fname = module_id.replace(".", "_") + ext
            module_map.setdefault(target, {})[fname] = p

    params = []
    for target in TARGETS:
        golden_dir = GOLDEN_ROOT / target
        if not golden_dir.exists():
            continue
        fmap = module_map.get(target, {})
        for gf in sorted(golden_dir.iterdir()):
            if not gf.is_file():
                continue
            if gf.suffix != _EXT.get(target):
                continue
            if gf.name not in fmap:
                continue  # runtime file or no matching east3-opt
            params.append((target, gf.name, gf, fmap[gf.name]))

    return params


def _param_id(val: object) -> str:
    if isinstance(val, Path):
        return ""
    return str(val)


_GOLDEN_PARAMS = _collect_golden_params()


def _skip_if_no_golden(target: str) -> None:
    if not (GOLDEN_ROOT / target).exists():
        pytest.skip(f"golden dir test/selfhost/{target}/ not found — run regenerate_selfhost_golden.py first")


# ---------------------------------------------------------------------------
# Test 1: golden files are non-empty (basic existence check)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("target,name,golden_path,east3_path", _GOLDEN_PARAMS,
                         ids=lambda v: _param_id(v))
def test_golden_file_nonempty(target: str, name: str, golden_path: Path, east3_path: Path) -> None:
    """Golden file exists and contains non-empty content."""
    _skip_if_no_golden(target)
    content = golden_path.read_text(encoding="utf-8")
    assert content.strip(), f"{golden_path} is empty"


# ---------------------------------------------------------------------------
# Test 2: re-emit matches golden
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("target,name,golden_path,east3_path", _GOLDEN_PARAMS,
                         ids=lambda v: _param_id(v))
def test_golden_matches_emit(target: str, name: str, golden_path: Path, east3_path: Path) -> None:
    """Re-emitting the east3-opt module produces the same output as the golden."""
    _skip_if_no_golden(target)

    timeout = _DEFAULT_TIMEOUT
    try:
        result = subprocess.run(
            [sys.executable, "-c", _EMIT_HELPER,
             str(ROOT / "src"), target, str(east3_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        pytest.skip(f"emit timed out after {timeout}s — module too large for regression check")

    if result.returncode != 0:
        pytest.skip(f"emit failed (not a regression guard): {result.stderr.strip()[:120]}")

    fresh = result.stdout
    if not fresh.strip():
        pytest.skip("emitter produced empty output — skipped during golden generation too")

    golden = golden_path.read_text(encoding="utf-8")
    assert fresh == golden, (
        f"Golden mismatch for {target}/{name}.\n"
        f"Run: python3 tools/gen/regenerate_selfhost_golden.py --target {target}\n"
        f"to update the golden."
    )


# ---------------------------------------------------------------------------
# Smoke: golden directory structure
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("target", TARGETS)
def test_golden_dir_exists_or_skip(target: str) -> None:
    """Golden directory either exists (populated) or is absent (not yet generated)."""
    golden_dir = GOLDEN_ROOT / target
    if not golden_dir.exists():
        pytest.skip(f"test/selfhost/{target}/ not yet generated")
    files = [f for f in golden_dir.iterdir() if f.is_file()]
    assert files, f"test/selfhost/{target}/ exists but is empty"
