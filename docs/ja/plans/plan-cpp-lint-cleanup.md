# 計画: C++ emitter hardcode lint 違反の解消 (P1-CPP-LINT-CLEANUP)

## 背景

`check_emitter_hardcode_lint.py --lang cpp` で 4 カテゴリ 14 件の違反が検出されている。

## 違反一覧

### 1. class_name (3件)

```
emitter.py:74:  "BaseException", "Exception", "ValueError", "TypeError", "IndexError",
emitter.py:1257: if attr == "add_argument" and owner_type == "ArgumentParser":
emitter.py:2658: if bn in ("BaseException", "Exception", "RuntimeError", ...)
```

- **74行目**: 例外クラス名のハードコードリスト。C++ の例外型マッピングに使われている
- **1257行目**: `ArgumentParser.add_argument` のメソッド名 + クラス名で分岐。EAST3 の `semantic_tag` or `runtime_call` で判定すべき
- **2658行目**: 例外基底クラスの判定。`bases` や `class_storage_hint` で判定するか、mapping.json の `types` テーブルで解決すべき

**対処方針**: 例外クラス名は mapping.json の `types` テーブルに既にあるのでそこから導出。`ArgumentParser` 分岐は EAST3 の解決済み情報を使う。

### 2. runtime_symbol (1件)

```
emitter.py:1489: if rc in ("py_print", "py_len") and len(arg_strs) >= 1:
```

- mapping.json 経由で解決済みの `runtime_call` 値を再度文字列マッチしている
- `call_adapters` 等で処理すべき

**対処方針**: `mapping.json` の `call_adapters` に `py_print: multi_arg_print` / `py_len: ref_arg` を追加し、emitter は adapter kind で分岐する。

### 3. type_id (1件)

```
emitter.py:2052: if tid == "" and expected_name.startswith("PYTRA_TID_"):
```

- type_id が空のとき `PYTRA_TID_*` プレフィックスで fallback している
- EAST3 / linker が type_id を確定すべきであり、emitter での fallback は §1.1 違反

**対処方針**: EAST3 / linker で type_id が確定していない場合のエラーハンドリングを改善し、emitter の fallback を除去。

### 4. skip_pure_python (9件)

```
mapping.json: skip_modules contains "pytra.std." which skips pure Python module pytra.std.{argparse,collections,env,json,pathlib,random,re,template,timeit}
```

- C++ は `pytra.std.` を丸ごと skip して全て native で持っている歴史的 debt
- pure Python モジュール（argparse, json, collections, pathlib, random, re, template, timeit, env）は transpile すべき

**対処方針**: `skip_modules` から `pytra.std.` の全 skip を撤廃し、`@extern` を持つモジュール（math, os, os_path, sys, glob, time）だけを個別に skip に列挙する。pure Python モジュールは transpile 対象にする。ただし C++ emitter の品質が transpile に耐えるか確認が必要なため、段階的に進める:

1. まず `pytra.std.env` / `pytra.std.template` / `pytra.std.timeit` (小さいモジュール) を skip から外して transpile 確認
2. 成功したら `pytra.std.random` / `pytra.std.collections` / `pytra.std.re` に拡大
3. 最後に `pytra.std.json` / `pytra.std.argparse` / `pytra.std.pathlib` (大きいモジュール)

## 影響範囲

- class_name / runtime_symbol / type_id の修正は emitter.py のみ
- skip_pure_python の修正は mapping.json + transpile 品質確認が必要
- fixture + sample parity の全件確認が必要

## 完了メモ

- `toolchain2.link.type_id` に built-in exception 判定 helper を追加し、C++ emitter の `BaseException` / `ValueError` 直書きを排除した
- `ArgumentParser.add_argument` の特殊整形は class 名ではなく `semantic_tag` と keyword call で判定するように変更した
- `mapping.json` に `call_adapters` を追加し、`py_print` / `py_len` の emit 分岐は adapter ベースへ移行した
- `PYTRA_TID_*` の prefix fallback は撤去し、EAST3 が渡す exact constant だけを明示マップで扱うよう整理した
- `skip_modules` から `pytra.std.` prefix を外し、native のまま維持すべき `@extern` モジュールのみを `skip_modules_exact` へ移した
- transpiled stdlib 経路で露出した regressions（`argparse_extended`, `json_extended`）も同時に修正し、`argparse/json/pathlib/re` の representative case を C++ parity で通した
