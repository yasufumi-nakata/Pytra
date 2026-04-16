<a href="../../en/todo/nim.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Nim backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-16

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 参考資料

- Nim emitter: `src/toolchain/emit/nim/`
- TS emitter（参考実装）: `src/toolchain/emit/ts/`
- Nim runtime: `src/runtime/nim/`
- emitter 実装ガイドライン: `docs/ja/spec/spec-emitter-guide.md`
- mapping.json 仕様: `docs/ja/spec/spec-runtime-mapping.md`

## 未完了タスク

### P1-EMITTER-SELFHOST-NIM: emit/nim/cli.py を単独で selfhost C++ build に通す

文脈: [docs/ja/plans/p1-emitter-selfhost-per-backend.md](../plans/p1-emitter-selfhost-per-backend.md)

各 backend emitter は subprocess で独立起動する自己完結プログラム。pytra-cli.py 全体の selfhost とは切り離し、`toolchain.emit.nim.cli` をエントリに単独で C++ build を通す。

1. [x] [ID: P1-EMITTER-SELFHOST-NIM-S1] `python3 src/pytra-cli.py -build src/toolchain/emit/nim/cli.py --target cpp -o work/selfhost/emit/nim/` を実行し、変換が通るようにする
   - 2026-04-16: nim/types.py の `_NIM_NORMALIZED_RESERVED` 末尾エントリの inline comment を literal 外へ移動（parser の `_join_continuation_lines` が joined 行内の `#` 以降を stripping して closing `}` が失われる問題を回避）。nim/cli.py を自己完結化し、typing.Callable を含む cli_runner.py に依存しないよう parse/load/module_id ロジックをインライン化。11 cpp ファイルの emit が通った。
2. [ ] [ID: P1-EMITTER-SELFHOST-NIM-S2] 生成された C++ を `g++ -std=c++20 -O0` でコンパイルを通す(source 側の型注釈不整合を修正)
   - 2026-04-16: 現状 blocker は emit/common/code_emitter.py に残る cpp emitter 側の未対応パターン（TS の S2 ブロッカーと同じ）。具体的には (a) `for alias in dict_var:` を subscript `dict[pair]` と誤変換、(b) `__file__` 参照が C++ `__FILE__` に解決されない、(c) `isinstance(info, dict)` narrowing 後の `info.get("module")` 型推論が JsonVal のまま。いずれも cpp emitter 側の改修が必要で、P20-CPP-SELFHOST (cpp.md) と重なる範囲。Nim 担当のスコープ外のため待機。
3. [ ] [ID: P1-EMITTER-SELFHOST-NIM-S3] コンパイル済み emitter で既存 fixture の manifest を処理し、Python 版 emitter と parity 一致を確認する


### P20-NIM-SELFHOST: Nim emitter で toolchain2 を Nim に変換し実行できるようにする

1. [ ] [ID: P20-NIM-SELFHOST-S0] selfhost 対象コードの型注釈補完（他言語と共通）
2. [ ] [ID: P20-NIM-SELFHOST-S1] toolchain2 全 .py を Nim に emit し、compile + 実行できることを確認する
3. [ ] [ID: P20-NIM-SELFHOST-S2] selfhost 用 Nim golden を配置する
4. [ ] [ID: P20-NIM-SELFHOST-S3] `run_selfhost_parity.py --selfhost-lang nim --emit-target nim --case-root fixture` で fixture parity PASS
5. [ ] [ID: P20-NIM-SELFHOST-S4] `run_selfhost_parity.py --selfhost-lang nim --emit-target nim --case-root sample` で sample parity PASS
