<a href="../../en/spec/spec-agent-planner.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# AI agent 運用仕様 — プランニング担当向け

このドキュメントは、TODO の起票・計画書の作成・タスク管理を担当する AI agent 向けのルールです。

## 1. TODO 起票のルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- **TODO に直接詳細を書かない。計画書（plans/）を先に作り、TODO からはそこへのリンクだけを貼る。**
- 着手対象は「未完了の最上位優先度 ID（最小 `P<number>`、同一優先度では上から先頭）」に固定し、明示上書き指示がない限り低優先度へ進まない。
- `P0` が 1 件でも未完了なら `P1` 以下には着手しない。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモ（件数等）を追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **emitter の parity テストは「emit 成功」ではなく「emit + compile + run + stdout 一致」を完了条件とする。**

## 2. 新機能と旧機能の撤去

- **新機能の導入タスクには、旧機能の撤去タスクも必ずセットで含めること。** 新しい仕組みを入れるだけで旧い仕組みの撤去を忘れると、旧コードが残り続けて二重管理やバグの原因になる。
- 撤去タスクは導入タスクの直後のサブタスクとして配置する。

## 3. 計画書の書き方

- `docs/ja/plans/` に `p<N>-<slug>.md` の形式で作成する。
- 必須セクション: 背景、サブタスク（ID 付き）、受け入れ基準、決定ログ。
- 対象 backend（C++, Go 等）を明記する。「各 emitter」のような曖昧な書き方は禁止。
- test/ への fixture 追加を忘れないこと。

## 4. 仕様書の更新

- 設計判断を行ったら、対応する spec/ ファイルに追記してからタスクを起票する。
- spec に書いていないルールを TODO やコードコメントで暗黙的に運用してはならない。

## 5. アーカイブ運用

- `docs/ja/todo/index.md` には未完了タスクのみを置く。
- セクション単位で完了した内容は `docs/ja/todo/archive/index.md`（索引）と `docs/ja/todo/archive/YYYYMMDD.md`（本文）へ移管する。

## 6. バージョン運用

- 内部バージョンゲート（`transpiler_versions.json`）は廃止済み。
- 対外リリース版は `docs/VERSION` で管理する。`PATCH` はエージェントが更新してよい。`MAJOR` / `MINOR` はユーザーの明示指示がある場合のみ。
