<a href="../../en/spec/spec-agent-coder.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# AI agent 運用仕様 — コード担当向け

このドキュメントは、コードの実装・修正・テストを担当する AI agent 向けのルールです。

## 1. golden / テスト生成

- **golden ファイル（east1/east2/east3/east3-opt/linked）は `python3 tools/regenerate_golden.py` でのみ生成すること。** `pytra-cli2` を直接叩いて手動で出力先を指定してはならない。手動生成はパスの間違い（`test/fixtures/` や `test/pytra/east1/built_in/` のような誤ったディレクトリ）の原因になる。
- **sample の再生成は `python3 tools/regenerate_samples.py` でのみ行うこと。**

## 2. test/ 配置ルール

- **`test/fixture/` 配下のディレクトリ構造を勝手に作らないこと。** 既存のディレクトリ構成（`source/py/`, `east1/py/`, `east2/`, `east3/`, `east3-opt/`, `linked/`）に従う。
- **`test/` 直下に新しいサブディレクトリを作らないこと**（`test/fixtures/` のような typo ディレクトリを防ぐ）。

## 3. emitter の禁止事項

- emitter は EAST3 を忠実にレンダリングする。以下は禁止:
  - cast を追加する（EAST に cast がないなら resolve のバグ）
  - 変数の型を変更する
  - for-range のループ変数の型を変更する
  - mapping.json にない名前変換をハードコードする
  - 型推論を再実装する
- **EAST の情報が不足している場合は、emitter にワークアラウンドを書くのではなく、EAST（resolve/compile/optimize）を修正すること。**
- 詳細は `docs/ja/spec/spec-emitter-guide.md` を参照。

## 4. runtime の禁止事項

- runtime ヘッダーに type_id テーブルのサイズや値をハードコードしてはならない（`g_type_table[4096]` のような固定サイズ配列は禁止）。
- 手書き TID 定数（`PYTRA_TID_VALUE_ERROR = 12` 等）は禁止。linker が生成した `pytra.built_in.type_id_table` の定数を使う。
- 正本ソース（`src/pytra/utils/*.py` 等）を変換器の制約に合わせて書き換えてはならない（例: `with` 文を手動 open/close に崩す）。emitter が対応するのが正しい対処。

## 5. コミット運用

- 作業内容が論理的にまとまった時点で、ユーザーの都度許可なしにコミットしてよい。
- コミットは論理単位で分割し、変更意図が分かるメッセージを付ける。
- TODO 消化コミットはメッセージに `ID` を含める（例: `[ID: P0-XXX-01] ...`）。
- **タスク完了時は `docs/ja/todo/index.md` の該当タスクの `[ ]` を `[x]` に変更し、完了メモ（件数等）を追記してコミットすること。** チェックを入れ忘れると、他のエージェントが同じタスクに着手してしまう。

## 6. バージョン更新

- 変換器関連ファイル（`src/py2*.py`, `src/pytra/**`, `src/toolchain/emit/**` 等）を変更する場合は、`src/toolchain/misc/transpiler_versions.json` の対応バージョンを **PATCH** で更新する。
- MINOR / MAJOR はユーザーの明示指示がある場合のみ。

## 7. selfhost 運用

- selfhost 対象コード（`src/toolchain/misc/east.py` 系）では、動的 import（`try/except ImportError` フォールバック、`importlib` による遅延 import）を使わない。
- selfhost 対象コードでは、Python 標準 `ast` モジュールへの依存を禁止する。
- トランスパイル対象の Python コードでは、Python 標準モジュール（`json`, `pathlib`, `sys` 等）の直接 `import` を禁止する。`pytra.std.*` を使う。
