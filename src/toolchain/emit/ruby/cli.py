"""Ruby backend CLI: manifest.json → Ruby multi-file output."""
from __future__ import annotations

from pathlib import Path

from toolchain.emit.common.cli_runner import run_emit_cli
from toolchain.emit.ruby.emitter import transpile_to_ruby


def _copy_ruby_runtime(output_dir: Path) -> None:
    """Copy Ruby runtime files into the emit directory."""
    runtime_root = Path("src").joinpath("runtime").joinpath("ruby")
    if not runtime_root.exists():
        return
    for bucket in ["built_in", "std"]:
        bucket_dir = runtime_root / bucket
        if not bucket_dir.exists():
            continue
        for runtime_file in bucket_dir.glob("*.rb"):
            dst = output_dir / bucket / runtime_file.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(runtime_file.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    import sys
    args: list[str] = []
    index = 1
    while index < len(sys.argv):
        args.append(sys.argv[index])
        index += 1
    return run_emit_cli(transpile_to_ruby, args, default_ext=".rb", post_emit=_copy_ruby_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
