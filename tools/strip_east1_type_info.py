#!/usr/bin/env python3
"""EAST1 golden file から型解決情報を除去し、spec-east1.md 準拠にする。

spec-east1.md の不変条件:
- resolved_type なし or "unknown"
- 型注釈はソースのまま（int→int64 の正規化をしない）
- runtime_module_id / runtime_symbol / semantic_tag なし
- casts は空リスト
- lowered_kind / builtin_name なし
- arg_usage なし
- yields_dynamic なし
- ForRange は生の Call(range) に戻す (※構文構造の変更は複雑なので、ForRange はそのまま残す)

使い方:
  python3 tools/strip_east1_type_info.py --input-dir test/sample/east1/py/ --output-dir test/sample/east1/py/
  python3 tools/strip_east1_type_info.py --input-dir test/fixture/east1/py/ --output-dir test/fixture/east1/py/
"""

from __future__ import annotations

import sys
import json
from pathlib import Path

# --- resolve の責務であり、EAST1 から除去するフィールド ---

# 式ノードから除去
_EXPR_REMOVE_FIELDS: set[str] = {
    "resolved_type",
    "type_expr",
    "type_expr_summary_v1",
    "runtime_module_id",
    "runtime_symbol",
    "semantic_tag",
    "runtime_call",
    "resolved_runtime_call",
    "resolved_runtime_source",
    "runtime_call_adapter_kind",
    "lowered_kind",
    "builtin_name",
    "yields_dynamic",
    "noncpp_module_id",
    "noncpp_runtime_call",
}

# FunctionDef から除去
_FUNCDEF_REMOVE_FIELDS: set[str] = {
    "arg_usage",
    "arg_type_exprs",
    "return_type_expr",
}

# Module meta から除去
_META_REMOVE_FIELDS: set[str] = {
    "dispatch_mode",
    "parser_backend",
}

# トップレベルから除去
_TOP_REMOVE_FIELDS: set[str] = {
    "schema_version",
}

# --- 型注釈の逆正規化: EAST 正規型 → Python ソースの型 ---

_DENORMALIZE_TYPES: dict[str, str] = {
    "int64": "int",
    "float64": "float",
    "uint8": "byte",
    "bool": "bool",
    "str": "str",
    "None": "None",
}


def _denormalize_type(t: str) -> str:
    """正規化済み型を Python ソース型に戻す。"""
    if t in _DENORMALIZE_TYPES:
        return _DENORMALIZE_TYPES[t]
    # list[int64] → list[int] 等
    if "[" in t:
        bracket = t.index("[")
        base = t[:bracket]
        inner = t[bracket + 1:-1]
        parts = _split_top_level(inner, ",")
        denormed = [_denormalize_type(p.strip()) for p in parts]
        return base + "[" + ", ".join(denormed) + "]"
    return t


def _split_top_level(text: str, sep: str) -> list[str]:
    """トップレベルのセパレータで分割（ネスト考慮）。"""
    out: list[str] = []
    depth = 0
    current = ""
    for ch in text:
        if ch == "[" or ch == "(":
            depth += 1
        elif ch == "]" or ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append(current)
            current = ""
        else:
            current += ch
    if current:
        out.append(current)
    return out


def strip_node(node: object) -> object:
    """再帰的に EAST1 不要フィールドを除去する。"""
    if isinstance(node, list):
        return [strip_node(item) for item in node]
    if not isinstance(node, dict):
        return node

    d: dict[str, object] = node
    kind = d.get("kind", "")
    result: dict[str, object] = {}

    for key, val in d.items():
        # 全ノード共通: resolve 責務のフィールドを除去
        if key in _EXPR_REMOVE_FIELDS:
            continue

        # FunctionDef 固有の除去
        if kind == "FunctionDef" and key in _FUNCDEF_REMOVE_FIELDS:
            continue

        # casts は空リストに
        if key == "casts":
            result["casts"] = []
            continue

        # arg_types: 正規化済み型をソース型に戻す（list or dict）
        if key == "arg_types":
            if isinstance(val, list):
                result["arg_types"] = [_denormalize_type(str(t)) if isinstance(t, str) else t for t in val]
            elif isinstance(val, dict):
                result["arg_types"] = {k: _denormalize_type(str(v)) if isinstance(v, str) else v for k, v in val.items()}
            else:
                result["arg_types"] = val
            continue

        # return_type: 正規化済み型をソース型に戻す
        if key == "return_type" and isinstance(val, str) and kind == "FunctionDef":
            result["return_type"] = _denormalize_type(val)
            continue

        # decl_type: 除去（resolve で付与）
        if key == "decl_type":
            continue

        # meta の処理
        if key == "meta" and isinstance(val, dict):
            meta_result: dict[str, object] = {}
            for mk, mv in val.items():
                if mk not in _META_REMOVE_FIELDS:
                    meta_result[mk] = strip_node(mv)
            result["meta"] = meta_result
            continue

        # トップレベルフィールドの除去
        if key in _TOP_REMOVE_FIELDS:
            continue

        # 再帰処理
        result[key] = strip_node(val)

    return result


def process_file(input_path: Path, output_path: Path) -> bool:
    """1 ファイルを処理する。"""
    try:
        text = input_path.read_text(encoding="utf-8")
        doc = json.loads(text)
        stripped = strip_node(doc)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(stripped, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return True
    except Exception as e:
        print(f"  FAIL: {input_path}: {e}", file=sys.stderr)
        return False


def main() -> int:
    input_dir_text = ""
    output_dir_text = ""

    i = 0
    args = sys.argv[1:]
    while i < len(args):
        tok = args[i]
        if tok == "--input-dir":
            if i + 1 >= len(args):
                print(f"error: missing value for {tok}", file=sys.stderr)
                return 1
            input_dir_text = args[i + 1]
            i += 2
            continue
        if tok == "--output-dir":
            if i + 1 >= len(args):
                print(f"error: missing value for {tok}", file=sys.stderr)
                return 1
            output_dir_text = args[i + 1]
            i += 2
            continue
        if tok == "-h" or tok == "--help":
            print("usage: strip_east1_type_info.py --input-dir DIR --output-dir DIR")
            print()
            print("examples:")
            print("  strip_east1_type_info.py --input-dir test/sample/east1/py/ --output-dir test/sample/east1/py/")
            print("  strip_east1_type_info.py --input-dir test/fixture/east1/py/ --output-dir test/fixture/east1/py/")
            return 0
        i += 1

    if input_dir_text == "" or output_dir_text == "":
        print("error: --input-dir and --output-dir are required", file=sys.stderr)
        return 1

    input_dir = Path(input_dir_text)
    output_dir = Path(output_dir_text)

    files = sorted(input_dir.rglob("*.py.east1"))
    if len(files) == 0:
        print(f"error: no .py.east1 files found in {input_dir}", file=sys.stderr)
        return 1

    print(f"strip: {len(files)} files, input={input_dir}, output={output_dir}")
    ok = 0
    fail = 0
    for f in files:
        rel = f.relative_to(input_dir)
        out = output_dir / rel
        if process_file(f, out):
            ok += 1
        else:
            fail += 1

    print(f"strip: {ok} ok, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
