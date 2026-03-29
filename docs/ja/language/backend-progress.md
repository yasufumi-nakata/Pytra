<a href="../../en/language/backend-progress.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# バックエンド進捗

## サポート状況

| | fixture parity | sample parity | selfhost |
|---|---|---|---|
| 詳細 | [fixture マトリクス](./backend-progress-fixture.md) | [sample マトリクス](./backend-progress-sample.md) | [selfhost マトリクス](./backend-progress-selfhost.md) |

## アイコン凡例

| アイコン | 意味 |
|---|---|
| 🟩 | PASS（emit + compile + run + stdout 一致） |
| 🟥 | FAIL（transpile_failed / run_failed / output_mismatch 等） |
| 🟨 | TM（toolchain_missing）/ emit OK（selfhost） |
| 🟪 | TO（timeout） |
| 🟧 | build OK（selfhost） |
| ⬜ | 未実行 / 未着手 |
| ⚠ | 結果が 7 日以上古い |

## 関連リンク

- [タスク一覧](../todo/index.md)
- [更新履歴](../changelog.md)
- [仕様書](../spec/index.md)

> fixture / sample / selfhost の各マトリクスは `python3 tools/gen/gen_backend_progress.py` で機械生成される。
