"""Julia backend CLI: manifest.json → Julia multi-file output."""
from __future__ import annotations

from pathlib import Path

from toolchain.emit.common.cli_runner import run_emit_cli
from toolchain.emit.julia.emitter import emit_julia_module


def _copy_julia_runtime(output_dir: Path) -> None:
    runtime_root = Path(__file__).resolve().parents[3] / "runtime" / "julia"
    if not runtime_root.exists():
        return
    for bucket in ("built_in", "std", "utils"):
        bucket_dir = runtime_root / bucket
        if not bucket_dir.exists():
            continue
        for runtime_file in bucket_dir.glob("*.jl"):
            dst = output_dir / bucket / runtime_file.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    import sys
    cli_argv: list[str] | None = sys.argv[1:]
    return run_emit_cli(emit_julia_module, cli_argv, default_ext=".jl", post_emit=_copy_julia_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
