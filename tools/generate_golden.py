#!/usr/bin/env python3
"""golden file 生成ツール: 現行 toolchain/ を使って各段の golden file を生成する。

pytra-cli2.py (selfhost 対象) とは分離された開発支援ツール。
toolchain/ に依存するため selfhost 非対象。

使い方:
  python3 tools/generate_golden.py --stage=east1 --from=python [-o test/east1/py/]
  python3 tools/generate_golden.py --stage=east2 --from=python [-o test/east2/py/]
  python3 tools/generate_golden.py --stage=east3 [-o test/east3/]
  python3 tools/generate_golden.py --stage=east3-opt [-o test/east3-opt/]

設計文書: docs/ja/plans/plan-pipeline-redesign.md §6.1
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

_GOLDEN_STAGES = ("east1", "east2", "east3", "east3-opt")

_GOLDEN_DEFAULT_OUTPUT: dict[str, str] = {
    "east1": "test/east1/py",
    "east2": "test/east2/py",
    "east3": "test/east3",
    "east3-opt": "test/east3-opt",
}

_GOLDEN_SAMPLE_DIR = "sample/py"


def _golden_output_filename(sample_stem: str, stage: str) -> str:
    """golden file のファイル名を返す。"""
    if stage == "east1":
        return sample_stem + ".py.east1"
    if stage == "east2":
        return sample_stem + ".east2"
    if stage == "east3" or stage == "east3-opt":
        return sample_stem + ".east3"
    return sample_stem + "." + stage


def _generate_east1(input_path: Path) -> dict[str, object]:
    """現行 toolchain/ で EAST1 を生成する。"""
    from toolchain.compile.core_entrypoints import convert_path
    from toolchain.compile.east1 import normalize_east1_root_document

    raw = convert_path(input_path, parser_backend="self_hosted")
    return normalize_east1_root_document(raw)


def _generate_east2(input_path: Path) -> dict[str, object]:
    """現行 toolchain/ で EAST2 を生成する。"""
    from toolchain.frontends.transpile_cli import load_east_document

    return load_east_document(input_path, parser_backend="self_hosted")


def _generate_east3(input_path: Path, opt_level: int) -> dict[str, object]:
    """現行 toolchain/ で EAST3 を生成する。"""
    from toolchain.frontends.transpile_cli import load_east3_document

    return load_east3_document(
        input_path,
        parser_backend="self_hosted",
        object_dispatch_mode="native",
        east3_opt_level=opt_level,
    )


def _generate_golden(input_path: Path, stage: str) -> dict[str, object]:
    """指定 stage の golden file を生成する。"""
    if stage == "east1":
        return _generate_east1(input_path)
    if stage == "east2":
        return _generate_east2(input_path)
    if stage == "east3":
        return _generate_east3(input_path, opt_level=0)
    if stage == "east3-opt":
        return _generate_east3(input_path, opt_level=1)
    raise ValueError(f"unknown stage: {stage}")


def main() -> int:
    stage = ""
    output_dir_text = ""
    sample_dir_text = _GOLDEN_SAMPLE_DIR

    i = 0
    args = sys.argv[1:]
    while i < len(args):
        tok = args[i]
        if tok == "--stage":
            if i + 1 >= len(args):
                print(f"error: missing value for {tok}", file=sys.stderr)
                return 1
            stage = args[i + 1]
            i += 2
            continue
        if tok.startswith("--stage="):
            stage = tok[len("--stage="):]
            i += 1
            continue
        if tok == "-o" or tok == "--output":
            if i + 1 >= len(args):
                print(f"error: missing value for {tok}", file=sys.stderr)
                return 1
            output_dir_text = args[i + 1]
            i += 2
            continue
        if tok == "--from":
            if i + 1 >= len(args):
                i += 1
                continue
            i += 2
            continue
        if tok.startswith("--from="):
            i += 1
            continue
        if tok == "--sample-dir":
            if i + 1 >= len(args):
                print(f"error: missing value for {tok}", file=sys.stderr)
                return 1
            sample_dir_text = args[i + 1]
            i += 2
            continue
        if tok == "-h" or tok == "--help":
            print("usage: generate_golden.py --stage=STAGE [-o OUTPUT_DIR] [--from=python]")
            print()
            print("stages: " + ", ".join(_GOLDEN_STAGES))
            print()
            print("examples:")
            print("  generate_golden.py --stage=east1 --from=python -o test/east1/py/")
            print("  generate_golden.py --stage=east2 --from=python -o test/east2/py/")
            print("  generate_golden.py --stage=east3 -o test/east3/")
            print("  generate_golden.py --stage=east3-opt -o test/east3-opt/")
            return 0
        i += 1

    if stage == "":
        print("error: --stage is required", file=sys.stderr)
        return 1
    if stage not in _GOLDEN_STAGES:
        print(f"error: unknown stage: {stage} (available: {', '.join(_GOLDEN_STAGES)})", file=sys.stderr)
        return 1

    if output_dir_text == "":
        output_dir_text = _GOLDEN_DEFAULT_OUTPUT[stage]
    output_dir = Path(output_dir_text)
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_dir = Path(sample_dir_text)
    samples = sorted(sample_dir.glob("*.py"))
    if len(samples) == 0:
        print(f"error: no .py files found in {sample_dir}", file=sys.stderr)
        return 1

    print(f"golden: stage={stage}, samples={len(samples)}, output={output_dir}")
    exit_code = 0
    ok_count = 0
    fail_count = 0
    for sample_path in samples:
        stem = sample_path.stem
        out_name = _golden_output_filename(stem, stage)
        out_path = output_dir / out_name
        try:
            doc = _generate_golden(sample_path, stage)
            out_path.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2, default=str) + "\n",
                encoding="utf-8",
            )
            print(f"  ok: {out_path}")
            ok_count += 1
        except Exception as e:
            print(f"  FAIL: {sample_path}: {e}", file=sys.stderr)
            fail_count += 1
            exit_code = 1

    print(f"golden: {ok_count} ok, {fail_count} failed")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
