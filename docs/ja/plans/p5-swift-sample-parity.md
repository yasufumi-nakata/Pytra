# P5: Swift sample parity

最終更新: 2026-03-21

関連 TODO:
- `docs/ja/todo/index.md` の `ID: P5-SWIFT-PARITY-*`

## 背景

pytra-cli の compile → link → emit パイプライン統一後、Swift backend の sample parity check を実施したところ 1/18 PASS（17番のみ）。

runtime コピー（`py_runtime.swift`）を `swift.py` に追加し、`pytra-cli.py` に `swiftc` 全 `.swift` 一括コンパイルの build/run を追加済み。`sample/swift/image_runtime.swift` は `py_runtime.swift` と関数が重複するためコピー対象から除外。

残り 17 件は全て transpile failed — emitter の未実装構文が原因。

## 対象

- `src/toolchain/emit/swift/emitter/` — emitter バグ修正
- `src/toolchain/emit/swift.py` — runtime コピー
- `src/pytra-cli.py` — Swift build/run

## 非対象

- Swift emitter の新規構文サポート追加（既存 sample で使われる範囲のみ）

## 受け入れ基準

- [ ] `runtime_parity_check.py --targets swift` で sample/py の全 18 ケースが PASS する。

## 決定ログ

- 2026-03-21: parity check 実施、1/18 PASS で起票。`image_runtime.swift` の重複関数問題を回避済み（コピー除外）。
- 2026-03-21: VarDecl 対応、`_resolved_runtime_symbol` の dotted call 修正、png/gif module rewrite 追加。4/18 PASS に改善。
- 2026-03-22: `build_import_alias_map` による stdlib 解決を実装。`@main struct Main` 除去。`_native` suffix 命名規約統一。**4/18 PASS**。残り: emitter 固有バグ多数。
- 2026-03-22: emitter バグ修正ラウンド2。修正: (1) IndentationError（L1074 残骸行削除）、(2) `_CLASS_BASES[cls_name]` → `_CLASS_BASES[0][cls_name]`（同 `_CLASS_METHODS`）、(3) `_MAIN_CALL_ALIAS` → `_MAIN_CALL_ALIAS[0]`、(4) `ForRange` ノード対応追加、(5) `is_entry` チェック追加（サブモジュールで `@main struct Main` 省略）、(6) `@extern` 関数 → `_native` 委譲生成、(7) `math.sqrt`/`math.pi` → Swift Foundation 関数にマッピング、(8) `png`/`gif` モジュール呼び出し解決、(9) `__pytra_bytearray`/`__pytra_bytes` を `py_runtime.swift` に追加。**1/18 PASS** (17番)。
  残りの課題:
  - built_in モジュール（`io_ops.swift` 等）の `@extern` 委譲が `io_ops_native_*` を呼ぶが、native ファイルが存在しない（`py_runtime.swift` に統合済み）。built_in の emit を抑制するか、`py_runtime.swift` 関数名と合わせる必要あり。
  - `__pytra_save_gif` 未定義（gif 出力関数が py_runtime にない）
  - `Int64` → `Int` 変換（Swift 配列 subscript は `Int` を期待）
  - `Any` → 具体型の自動キャスト不足
  - `__pytra_dict_get` 未定義
  - `tmp` 変数スコープ問題（sample 12）
