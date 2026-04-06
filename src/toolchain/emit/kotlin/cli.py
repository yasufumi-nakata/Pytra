"""Kotlin backend CLI: manifest.json → Kotlin multi-file output."""
from __future__ import annotations

from pytra.std.pathlib import Path

from toolchain.emit.common.cli_runner import run_emit_cli
from toolchain.emit.kotlin.emitter import emit_kotlin_module


def _copy_kotlin_runtime(output_dir: Path) -> None:
    """Copy Kotlin runtime files into the emit directory."""
    runtime_root = Path(__file__).resolve().parents[3].joinpath("runtime").joinpath("kotlin")
    if not runtime_root.exists():
        return
    for bucket in ["built_in", "std"]:
        bucket_dir = runtime_root.joinpath(bucket)
        if not bucket_dir.exists():
            continue
        for kt_file in bucket_dir.glob("*.kt"):
            dst = output_dir.joinpath(kt_file.name)
            dst.write_text(kt_file.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    import sys
    return run_emit_cli(emit_kotlin_module, sys.argv[1:], default_ext=".kt", post_emit=_copy_kotlin_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
