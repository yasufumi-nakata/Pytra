#!/usr/bin/env python3
"""pytra-cli2: 新パイプライン CLI (parse / resolve / optimize / emit).

設計文書: docs/ja/plans/plan-pipeline-redesign.md

使い方:
  pytra-cli2 -parse INPUT.py [-o OUTPUT.py.east1]
  pytra-cli2 -parse INPUT.py INPUT2.py ...          # 複数ファイル一括

将来追加予定:
  pytra-cli2 -resolve --from=python *.py.east1
  pytra-cli2 -optimize *.east2
  pytra-cli2 -emit --target=cpp *.east3
  pytra-cli2 -build --target=cpp INPUT.py
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# parse: .py → .py.east1
# ---------------------------------------------------------------------------

def _default_east1_output_path(input_path: Path) -> Path:
    """a.py → a.py.east1 (同一ディレクトリ)"""
    return input_path.parent / (input_path.name + ".east1")


def _parse_one(input_path: Path, output_path: Path | None, pretty: bool) -> int:
    """1 ファイルを parse して .py.east1 を生成する。"""
    if not input_path.exists():
        print(f"error: file not found: {input_path}", file=sys.stderr)
        return 1

    # PYTHONPATH=src 前提で toolchain を import
    from toolchain.compile.core_entrypoints import convert_path
    from toolchain.compile.east1 import normalize_east1_root_document

    try:
        raw_east = convert_path(input_path, parser_backend="self_hosted")
    except Exception as e:
        print(f"error: parse failed: {input_path}: {e}", file=sys.stderr)
        return 1

    east1_doc = normalize_east1_root_document(raw_east)

    if output_path is None:
        output_path = _default_east1_output_path(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if pretty else None
    output_path.write_text(
        json.dumps(east1_doc, ensure_ascii=False, indent=indent) + "\n",
        encoding="utf-8",
    )
    print(f"parsed: {output_path}")
    return 0


def cmd_parse(args: list[str]) -> int:
    """parse サブコマンド: .py → .py.east1"""
    inputs: list[str] = []
    output_text = ""
    pretty = False

    i = 0
    while i < len(args):
        tok = args[i]
        if tok == "-o" or tok == "--output":
            if i + 1 >= len(args):
                print(f"error: missing value for {tok}", file=sys.stderr)
                return 1
            output_text = args[i + 1]
            i += 2
            continue
        if tok == "--pretty":
            pretty = True
            i += 1
            continue
        if tok == "-h" or tok == "--help":
            print("usage: pytra-cli2 -parse INPUT.py [-o OUTPUT.py.east1] [--pretty]")
            print("       pytra-cli2 -parse INPUT1.py INPUT2.py ...  (multiple files)")
            return 0
        if not tok.startswith("-"):
            inputs.append(tok)
        i += 1

    if len(inputs) == 0:
        print("error: at least one input file is required", file=sys.stderr)
        return 1

    # -o は単一ファイルのときのみ有効
    if output_text != "" and len(inputs) > 1:
        print("error: -o cannot be used with multiple input files", file=sys.stderr)
        return 1

    exit_code = 0
    for inp in inputs:
        input_path = Path(inp)
        out = Path(output_text) if output_text != "" else None
        rc = _parse_one(input_path, out, pretty)
        if rc != 0:
            exit_code = rc
    return exit_code


# ---------------------------------------------------------------------------
# resolve: *.py.east1 → *.east2 (未実装)
# ---------------------------------------------------------------------------

def cmd_resolve(args: list[str]) -> int:
    print("error: -resolve is not yet implemented", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# optimize: *.east2 → *.east3 (未実装)
# ---------------------------------------------------------------------------

def cmd_optimize(args: list[str]) -> int:
    print("error: -optimize is not yet implemented", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# emit: *.east3 → target (未実装)
# ---------------------------------------------------------------------------

def cmd_emit(args: list[str]) -> int:
    print("error: -emit is not yet implemented", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# build: .py → target (一括実行, 未実装)
# ---------------------------------------------------------------------------

def cmd_build(args: list[str]) -> int:
    print("error: -build is not yet implemented", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

_COMMANDS = {
    "-parse": cmd_parse,
    "-resolve": cmd_resolve,
    "-optimize": cmd_optimize,
    "-emit": cmd_emit,
    "-build": cmd_build,
}


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: pytra-cli2 <command> [options]")
        print()
        print("commands:")
        print("  -parse      .py → .py.east1         (parse)")
        print("  -resolve    *.py.east1 → *.east2    (type resolve + normalize)")
        print("  -optimize   *.east2 → *.east3       (whole-program optimization)")
        print("  -emit       *.east3 → target         (code generation)")
        print("  -build      .py → target             (all-in-one)")
        return 0

    cmd_name = argv[0]
    cmd_fn = _COMMANDS.get(cmd_name)
    if cmd_fn is None:
        print(f"error: unknown command: {cmd_name}", file=sys.stderr)
        print("run 'pytra-cli2 --help' for available commands", file=sys.stderr)
        return 1

    return cmd_fn(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
