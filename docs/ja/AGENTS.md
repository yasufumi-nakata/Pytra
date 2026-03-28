<a href="../en/AGENTS.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# エージェント運用ルール（ブートストラップ）

このファイルは最初に読む入口だけを定義します。  
詳細ルールの正本は `docs/ja/spec/spec-agent.md` です。

## 起動時に読む順序

1. `docs/ja/spec/index.md`
2. `docs/ja/spec/spec-agent.md`
3. `docs/ja/todo/index.md`

## 最小ルール（全員共通）

- `docs/ja/` を正本（source of truth）とし、`docs/en/` は翻訳ミラー。
- 作業生成物は `work/tmp/`、selfhost テストは `work/selfhost/`。
- **出力禁止先**: `out/`, `selfhost/`, `sample/obj/`, `/tmp/`。
- `materials/` は read-only（明示指示がある場合のみ編集可）。

## git 禁止事項（全員共通）

- **`git stash` / `git checkout --` / `git restore` / `git reset --hard` / `git clean -f` は禁止。**
- **`.git/index.lock` を削除してはならない。** 他のインスタンスが操作中なので **待つ**。

## 役割別の詳細ルール

| 役割 | ファイル | 内容 |
|---|---|---|
| プランニング担当 | [spec-agent-planner.md](./spec/spec-agent-planner.md) | TODO 起票、計画書、撤去タスク義務、バージョン運用 |
| コード担当 | [spec-agent-coder.md](./spec/spec-agent-coder.md) | golden 生成、test 配置、emitter/runtime 禁止事項、コミット運用 |
| 共通詳細 | [spec-agent.md](./spec/spec-agent.md) | ドキュメント言語運用、全般ルール |

## 参照先

- TODO: `docs/ja/todo/index.md`
- TODO 履歴: `docs/ja/todo/archive/index.md`
