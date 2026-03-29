<a href="../../en/spec/spec-tools-update-rules.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# `tools/` — 更新ルール

[索引に戻る](./spec-tools.md)

- `tools/` に新しいスクリプトを追加した場合は、`docs/ja/spec/spec-tools.md`（索引）を同時に更新します。
- スクリプトの目的は「何を自動化するために存在するか」を 1 行で明記します。
- 破壊的変更（引数仕様の変更、廃止、統合）がある場合は、`docs/ja/tutorial/how-to-use.md` の関連コマンド例も同期更新します。
- 内部バージョンゲート（`transpiler_versions.json`）は廃止済み。対外リリース版は `docs/VERSION` で手動管理する。
- sample 再生成は parity check の結果で検証する。
