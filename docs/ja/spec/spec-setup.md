<a href="../../en/spec/spec-setup.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 開発環境セットアップ

このドキュメントは、git clone 直後にローカル開発環境を動作可能な状態にするための手順をまとめたものです。

## 1. 前提

- Python 3.10 以上
- g++（C++ parity を確認する場合）
- `PYTHONPATH=src` を設定する（各コマンドで明示するか、シェルで export する）

## 2. golden ファイルの生成

golden ファイル（east1/east2/east3/east3-opt/linked/selfhost）は git 管理していない（`.gitignore` 対象）。clone 直後はローカルに存在しないため、以下を実行して生成する。

```bash
PYTHONPATH=src python3 tools/gen/regenerate_golden.py
```

これで fixture / sample / stdlib / pytra の全段 golden が生成される。parity check はこの golden に依存するため、先に実行すること。

**注意: golden が既に存在する場合は再生成してはならない。** 他の agent が作業中に再生成すると golden が上書きされ、テスト結果が変わる。再生成が必要な場合はユーザーの指示を受けること。

## 3. runtime east キャッシュの生成

`src/runtime/east/` は `src/pytra/{built_in,std,utils}/*.py` から生成されるキャッシュで、linker がマルチモジュール連結時に stdlib の型情報を解決するために参照する。こちらも git 管理していない。

```bash
PYTHONPATH=src python3 tools/check/check_east3_golden.py --check-runtime-east --update
```

### 鮮度チェック

`src/pytra/` 配下の Python 正本を変更した場合、runtime east が stale になる可能性がある。`--update` を外すと差分チェックのみを行う:

```bash
PYTHONPATH=src python3 tools/check/check_east3_golden.py --check-runtime-east
```

## 4. 実行順序のまとめ

clone 直後に以下の順で実行する:

```bash
# 1. golden 生成
PYTHONPATH=src python3 tools/gen/regenerate_golden.py

# 2. runtime east 生成
PYTHONPATH=src python3 tools/check/check_east3_golden.py --check-runtime-east --update

# 3. parity check（例: C++）
PYTHONPATH=src:tools/check python3 tools/check/runtime_parity_check_fast.py --targets cpp
```

## 5. 注意事項

- golden も runtime east も、通常の開発作業中は既に生成済みの状態で存在する。毎回再生成する必要はない。
- 再生成が必要になるのは clone 直後、またはソース変更で stale になったときのみ。
- golden をコミットしてはならない。手動編集も禁止。
- 正本ツールの詳細は [spec-tools.md](./spec-tools.md) を参照。
