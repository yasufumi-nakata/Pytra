<a href="../../en/todo/index.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO（未完了）

> `docs/ja/` が正（source of truth）です。`docs/en/` はその翻訳です。

最終更新: 2026-03-29

## 文脈運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 各領域の agent は自分の領域ファイル内で優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモ（件数等）を追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **emitter の parity テストは「emit 成功」ではなく「emit + compile + run + stdout 一致」を完了条件とする。** emit だけ成功してもプレースホルダーコードが混入している可能性がある。
- **タスク詳細は領域別ファイルに記載する。** この index.md は優先度一覧と領域リンクのみ保持する。

## 領域別 TODO

| 領域 | ファイル |
|---|---|
| C++ backend | [cpp.md](./cpp.md) |
| Go backend | [go.md](./go.md) |
| Rust backend | [rust.md](./rust.md) |
| TS/JS backend | [ts.md](./ts.md) |
| インフラ・ツール | [infra.md](./infra.md) |

注: 完了済みタスクは [アーカイブ](archive/index.md) に移動済み。
