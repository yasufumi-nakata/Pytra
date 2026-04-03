<a href="../../en/todo/rust.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Rust backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-03

## 運用ルール

- **旧 toolchain1（`src/toolchain/emit/rs/`）は変更不可。** 新規開発・修正は全て `src/toolchain2/emit/rs/` で行う（[spec-emitter-guide.md](../spec/spec-emitter-guide.md) §1）。
- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 現状

- toolchain2 の Rust emitter は `src/toolchain2/emit/rs/` に実装済み（fixture 131/131 + sample 18/18 emit 成功）
- runtime は `src/runtime/rs/` に存在（toolchain2 向けに拡張中）
- compile + run parity は一部 fixture で PASS（class_instance, dataclass, class_tuple_assign, nested_types, str_index_char_compare 等）
- 残ブロッカー: 継承 + ref セマンティクスの EAST3 側問題（P0-EAST3-INHERIT）

## 未完了タスク

### P5-RS-CLI-COMMON: Rust cli.py を共通ランナーに移行する

文脈: [docs/ja/plans/p5-rs-cli-common-runner.md](../plans/p5-rs-cli-common-runner.md)

全17言語中 Rust のみ独自 cli.py（235行）。type_id テーブル廃止（P0-RS-TYPEID-CLN）後に共通ランナーへ移行可能。

前提: P0-RS-TYPEID-CLN 完了（type_id テーブル不要化）

1. [x] [ID: P5-RS-CLI-S1] Rust emitter を `expected_type_name` ベースに移行する
   - 完了: Rust emitter の `isinstance` / class hierarchy 判定は `expected_type_name` fallback と `PyAny::TypeId` / downcast ベースに整理済みで、manifest type-id table を前提にしない形へ移行した。
2. [x] [ID: P5-RS-CLI-S2] `_generate_type_id_table_rs` と `_manifest_type_id_table` を削除する
   - 完了: [cli.py](../../src/toolchain2/emit/rs/cli.py) から Rust 独自の type-id table 生成を削除した。
3. [x] [ID: P5-RS-CLI-S3] runtime コピーと package mode を `post_emit` に移動し、共通ランナーに委譲する
   - 完了: Rust `cli.py` を `run_emit_cli(...)` ベースへ移行し、runtime コピーと `--package` の `Cargo.toml` / `src/lib.rs` / `src/main.rs` 生成を `post_emit` 側へ移した。`pytra-cli2 -build ... --target rs` と `--rs-package` の両方で emit 成功を確認。
4. [x] [ID: P5-RS-CLI-S4] Rust parity に回帰がないことを確認する
   - 完了: broad parity は `P0-RS-TYPEID-CLN-S3` で `stdlib 16/16 PASS`, `sample 18/18 PASS`, `fixture 145/145 PASS` を確認済み。CLI 共通化後も `runtime_parity_check_fast --case-root fixture --targets rs top_level union_basic optional_none` が `3/3 PASS` で、spot check に回帰がないことを確認。

### P9-RS-SELFHOST: Rust emitter で toolchain2 を Rust に変換し cargo build を通す

前提: P7-RS-EMITTER 完了後に着手。

1. [x] [ID: P9-RS-SELFHOST-S0] selfhost 対象コード（`src/toolchain2/` 全 .py）で戻り値型の注釈が欠けている関数に型注釈を追加する — resolve が `inference_failure` にならない状態にする（P4/P6/P20 と共通。先に完了した側の成果を共有）
   - 完了: `python3 -m unittest tools.unittest.selfhost.test_selfhost_return_annotations` で `src/toolchain2/` の戻り値注釈欠落が 0 件であることを確認。
2. [ ] [ID: P9-RS-SELFHOST-S1] flat `include!` を Rust `mod` + `use` 構造に置換する — 文脈: [plan-rs-selfhost-mod-structure.md](../plans/plan-rs-selfhost-mod-structure.md)
   - [ ] [ID: P9-RS-MOD-S1] Rust emitter の multifile_writer に mod 構造出力モードを追加する（1 EAST module = 1 Rust mod）
   - [ ] [ID: P9-RS-MOD-S2] `lib.rs` / `Cargo.toml` の自動生成を実装する
   - [ ] [ID: P9-RS-MOD-S3] cross-module `use crate::` パスの emit を実装する
3. [ ] [ID: P9-RS-SELFHOST-S2] toolchain2 全 .py を Rust に emit し、cargo build が通ることを確認する
4. [ ] [ID: P9-RS-SELFHOST-S3] cargo build 失敗ケースを emitter/runtime の修正で解消する（EAST の workaround 禁止）
5. [ ] [ID: P9-RS-SELFHOST-S4] selfhost 用 Rust golden を配置し、回帰テストとして維持する
6. [ ] [ID: P9-RS-SELFHOST-S5] `run_selfhost_parity.py --selfhost-lang rs --emit-target rs --case-root fixture` で fixture parity PASS
7. [ ] [ID: P9-RS-SELFHOST-S6] `run_selfhost_parity.py --selfhost-lang rs --emit-target rs --case-root sample` で sample parity PASS
