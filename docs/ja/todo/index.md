# TODO（未完了）

> `docs/ja/` が正（source of truth）です。`docs/en/` はその翻訳です。

<a href="../../en/todo/index.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

最終更新: 2026-03-19（5 件追加）

## 文脈運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度上書きは `docs/ja/plans/instruction-template.md` 形式でチャット指示し、`todo2.md` は使わない。
- 着手対象は「未完了の最上位優先度ID（最小 `P<number>`、同一優先度では上から先頭）」に固定し、明示上書き指示がない限り低優先度へ進まない。
- `P0` が 1 件でも未完了なら `P1` 以下には着手しない。
- 着手前に文脈ファイルの `背景` / `非対象` / `受け入れ基準` を確認する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める（例: ``[ID: P0-XXX-01] ...``）。
- `docs/ja/todo/index.md` の進捗メモは 1 行要約に留め、詳細（判断・検証ログ）は文脈ファイル（`docs/ja/plans/*.md`）の `決定ログ` に記録する。
- 1 つの `ID` が大きい場合は、文脈ファイル側で `-S1` / `-S2` 形式の子タスクへ分割して進めてよい（親 `ID` 完了までは親チェックを維持）。
- 割り込み等で未コミット変更が残っている場合は、同一 `ID` を完了させるか差分を戻すまで別 `ID` に着手しない。
- `docs/ja/todo/index.md` / `docs/ja/plans/*.md` 更新時は `python3 tools/check_todo_priority.py` を実行し、差分に追加した進捗 `ID` が最上位未完了 `ID`（またはその子 `ID`）と一致することを確認する。
- 作業中の判断は文脈ファイルの `決定ログ` へ追記する。
- 一時出力は既存 `out/`（または必要時のみ `/tmp`）を使い、リポジトリ直下に新規一時フォルダを増やさない。

## メモ

- このファイルは未完了タスクのみを保持します。
- 完了済みタスクは `docs/ja/todo/archive/index.md` 経由で履歴へ移動します。
- `docs/ja/todo/archive/index.md` は索引のみを保持し、履歴本文は `docs/ja/todo/archive/YYYYMMDD.md` に日付単位で保存します。

## 未完了タスク

### P0: 緊急修正

#### P0-1: inline union を tagged struct に統一

1. [x] [ID: P0-INLINE-UNION-TAGGED-STRUCT-01] inline union を tagged struct に統一。

#### P0-3: パーサーの型エイリアス展開を抑止

2. [ ] [ID: P0-TYPE-ALIAS-NO-EXPAND-01] EAST1 パーサーが `type X = T` で登録した型エイリアスを `_sh_ann_to_type` で展開しないようにする。`v: JsonVal` の `resolved_type` はエイリアス名 `"JsonVal"` のまま EAST IR に残す。P1-JSON-TAGGED-UNION-REWRITE-01 のブロッカー。 引数型注釈等の inline union（`str | Path` 等）を `std::variant` ではなく tagged struct として emit する。名前は `_Union_` + メンバ型名で自動生成し、同一 union 型は同一 struct を再利用する。pathlib.py の `str | Path` 対応はこのタスク完了後に実施する。

### P1: 言語機能追加

#### P1-1: json.py を type JsonVal = ... で書き直し

文脈: [docs/ja/plans/p1-json-tagged-union-rewrite.md](../plans/p1-json-tagged-union-rewrite.md)

1. [ ] [ID: P1-JSON-TAGGED-UNION-REWRITE-01] `json.py` を `type JsonVal = None | bool | int | float | str | list[JsonVal] | dict[str, JsonVal]` で書き直し、再帰的 tagged union の実用検証を行う。P0-INLINE-UNION 完了が前提。

### P2: compile / link パイプライン分離

#### P2-1: compile / link 2段パイプライン

文脈: [docs/ja/plans/p2-compile-link-pipeline.md](../plans/p2-compile-link-pipeline.md)

1. [ ] [ID: P2-COMPILE-LINK-PIPELINE-01] 単一ファイルモードを廃止し全パスを compile → link 経由に統一する。type_id を linker で DFS 確定し、`PYTRA_TID_*` 定数・実行時レジストリを廃止する。

### P3: コード品質改善

#### P3-1: from __future__ import annotations の廃止検討

文脈: [docs/ja/plans/p3-future-annotations-removal.md](../plans/p3-future-annotations-removal.md)

1. [x] [ID: P3-FUTURE-ANNOTATIONS-REMOVAL-01] パーサーがアノテーションを自前でパースするため `from __future__ import annotations` が不要か検証し、不要であれば `src/pytra/` から削除する。

#### P3-2: predicates.py の @template 化（Any 除去）

文脈: [docs/ja/plans/p3-predicates-template.md](../plans/p3-predicates-template.md)

2. [x] [ID: P3-PREDICATES-TEMPLATE-01] `py_any` / `py_all` を `Any` 引数から `@template("T")` に変更し、テンプレート関数として生成する。`src/pytra/built_in/predicates.py` から `Any` を除去する。

### P4: テスト修正

#### P4-1: pre-existing テスト失敗の修正

文脈: [docs/ja/plans/p4-preexisting-test-failures-fix.md](../plans/p4-preexisting-test-failures-fix.md)

1. [x] [ID: P4-PREEXISTING-TEST-FAILURES-FIX-01] 3件修正、1件 skip（P2 で根本修正）。 `test_py2cpp_features.py` の 4 件の pre-existing テスト失敗を修正する。

### P5: バックエンド修正

#### P5-1: Lua バックエンドの emit 失敗修正

文脈: [docs/ja/plans/p5-lua-backend-emit-fix.md](../plans/p5-lua-backend-emit-fix.md)

1. [x] [ID: P5-LUA-BACKEND-EMIT-FIX-01] P0 inline union 修正で解消。Lua generated 追加。 Lua バックエンドで `pytra.std.collections` (Deque) の transpile が空出力になる問題を修正する。

### P6: ランタイム最適化

#### P6-1: CPP_HEADER の固定 include を必要性判定に変更

1. [x] [ID: P6-CPP-INCLUDE-OPTIMIZE-01] C++ 生成コード冒頭の `#include` を固定文字列ではなく、emitter が生成コードの内容に応じて必要な include のみを emit するよう変更する。

#### P6-2: Deque をネイティブ型にマッピング

2. [ ] [ID: P6-DEQUE-NATIVE-MAPPING-01] ネイティブ deque を持つバックエンドで、`Deque` クラスを list ベース実装ではなく言語ネイティブの deque 型に emit するよう emitter を改良する。C++ は `std::deque` で対応済み。Rust(`VecDeque`), Java/Kotlin(`ArrayDeque`), Scala(`ArrayDeque`), Nim(`Deque`), PHP(`SplDoublyLinkedList`) が対象。

### P7: selfhost 完全自立化

#### P7-1: native/compiler/ 完全削除

文脈: [docs/ja/plans/p7-selfhost-native-compiler-elim.md](../plans/p7-selfhost-native-compiler-elim.md)

1. [ ] [ID: P7-SELFHOST-NATIVE-COMPILER-ELIM-01] `src/runtime/cpp/native/compiler/` を完全削除し、selfhost バイナリがホスト Python をシェルアウトなしで動作できるようにする。
