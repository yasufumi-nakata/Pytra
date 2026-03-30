<a href="../../en/todo/go.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Go backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-30（P0-GO-ENV-TARGET 完了、P0-GO-TYPE-MAPPING 完了、P0-GO-SPLITEXT 完了、P0-GO-ARGPARSE-ARGV 完了、stdlib 16/16 PASS）

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 未完了タスク

### P0-GO-SPLITEXT: `py_splitext` が multi-return を返さず fixture parity FAIL

原因: `src/runtime/go/std/pathlib_native.go` の `py_splitext` が `[]any` を返しているが、emitter は `(root, ext) = os.path.splitext(...)` を 2変数アンパックとして emit する。Go では multi-return 関数 `(string, string)` が必要。

1. [x] [ID: P0-GO-SPLITEXT-S1] `py_splitext` のシグネチャを `(string, string)` に変更し、emit 側の2変数アンパックと整合させる
   - 完了: `pathlib_native.go` の `splitext` / `py_splitext` を `(string, string)` 返しに変更
2. [x] [ID: P0-GO-SPLITEXT-S2] `os_glob_extended:go` parity PASS を確認する
   - 完了: PASS

### P0-GO-ARGPARSE-ARGV: `parse_args` が `[]string` を `*PyList[string]` に代入できず parity FAIL

原因: emitter の `__LIST_CTOR__` が `list(x)` を `append([]T{}, x.items...)` と emit し `[]T` を返すが、代入先の `args` が `*PyList[string]` 型のため型不一致。

1. [x] [ID: P0-GO-ARGPARSE-S1] `__LIST_CTOR__` で `list(x)` の結果を `PyListFromSlice[T](append(...))` に wrap するよう修正する
   - 完了: `emitter.py` の `__LIST_CTOR__` ハンドラで `result_type.startswith("list[")` 時に `PyListFromSlice[T]()` でラップ
2. [x] [ID: P0-GO-ARGPARSE-S2] `argparse_extended:go` parity PASS を確認する
   - 完了: PASS

### P0-GO-SPLITEXT（副作用修正）: `py_splitext` を `(string, string)` に変更したことで既存 parity が破損 → tuple-multi-return 展開で解消

原因: `pathlib.py` は `__tup_N = py_splitext(...)` + `__tup_N[0]` 形式（`Assign` + subscript）で使用していたが、`py_splitext` が `(string, string)` を返すと `var __tup_N []any = py_splitext(...)` が Go コンパイルエラーになる。

修正:
- `_emit_assign` で `target: Name(resolved_type=tuple[...])` かつ `value: Call(resolved_type=tuple[...])` のとき、多値変数 `__tup_N_0, __tup_N_1 := py_splitext(...)` に展開し `ctx.tup_multi_vars["__tup_N"] = ["__tup_N_0", "__tup_N_1"]` を記録
- `_emit_subscript` で `value` が `ctx.tup_multi_vars` にある場合、インデックスに対応する変数名 `__tup_N_i` を直接返す
- `EmitContext.tup_multi_vars: dict[str, list[str]]` を追加
- stdlib 16/16 PASS 回復（2026-03-30）

### P0-GO-TYPE-MAPPING: Go emitter の型写像を mapping.json に移行する

仕様: [spec-runtime-mapping.md](../spec/spec-runtime-mapping.md) §7

1. [x] [ID: P0-GO-TYPEMAP-S1] `src/runtime/go/mapping.json` に `types` テーブルを追加する — POD 型（`int64` → `int64` 等）とクラス型（`Exception` → `*PytraErrorCarrier` 等）の全写像を定義する
   - 完了: `mapping.json` に `types` テーブル追加（`_TYPE_MAP` の全 34 エントリを JSON へ）
2. [x] [ID: P0-GO-TYPEMAP-S2] Go emitter の型名ハードコード（`types.py` 含む）を `resolve_type()` 呼び出しに置換する
   - 完了: `RuntimeMapping.types` フィールド追加、`load_runtime_mapping` で読み込み、`resolve_type()` 関数追加（`code_emitter.py`）、`go_type()` に `type_map` 引数追加して `mapping.types` を優先ルックアップ（`types.py`）、`_go_type_with_ctx` が `ctx.mapping.types` を渡す（`emitter.py`）
3. [x] [ID: P0-GO-TYPEMAP-S3] fixture parity に影響がないことを確認する
   - 完了: fixture 146 件中 144 PASS、fail=2 は既存 stdlib の pre-existing failures（argparse_extended, os_glob_extended）で変化なし

### P1-GO-CONTAINER-WRAPPER: Go emitter の container 既定表現を spec 準拠に修正する

文脈: `docs/ja/spec/spec-emitter-guide.md` §10

1. [x] [ID: P1-GO-CONTAINER-S1] Go emitter の全コードパス（リテラル生成、関数引数、戻り値、ループ変数、代入等）で list/dict/set を既定で参照型ラッパー（`*PyList[T]`, `*PyDict[K,V]`, `*PySet[T]`）にする。値型（`[]T`, `map[K]V`）が混在している箇所を全て修正する
   - 完了: `_wrap_ref_container_value_code`, `_go_ref_container_type`, optional container 対応, cross-module method call args wrapping, TupleUnpack 宣言修正 等
2. [x] [ID: P1-GO-CONTAINER-S2] `meta.linked_program_v1.container_ownership_hints_v1.container_value_locals_v1` ヒントがある局所変数のみ値型縮退を許可する
   - 完了: `_prefer_value_container_local` が `container_value_locals_v1` ヒントを参照して値型縮退を制御
3. [x] [ID: P1-GO-CONTAINER-S3] Go runtime ヘルパー（`PyListConcat`, `PyListExtend` 等）が全て `*PyList[T]` を受け取る形に統一する
   - 完了: `py_runtime.go` の全ヘルパーが `*PyList[T]` / `*PyDict[K,V]` / `*PySet[T]` を受け取る形に統一済み
4. [x] [ID: P1-GO-CONTAINER-S4] fixture 132 件 + sample 18 件の Go compile + run parity を通す
   - fixture: 147 件全 PASS（core 22, oop 18, typing 22, strings 12, collections 20, control 16, stdlib 16, imports 7, signature 13, trait_basic 1）
   - sample: 18 件全 PASS（2026-03-29 確認）
   - 完了: `_wrap_ref_container_value_code` を Call が container 型を返す場合はスキップ、`_emit_return` の multi_return pass-through、`_emit_multi_assign` の `tuple[...]` Call 対応、`var_decl_depth` による Go ブロックスコープ変数宣言追跡、type assertion statement の `_ = ` 前置

### P5-COMMON-RENDERER-GO: Go emitter の CommonRenderer 移行 + fixture parity

文脈: [docs/ja/plans/p2-lowering-profile-common-renderer.md](../plans/p2-lowering-profile-common-renderer.md)
仕様: [docs/ja/spec/spec-language-profile.md](../spec/spec-language-profile.md) §8

1. [x] [ID: P5-CR-GO-S1] Go emitter を CommonRenderer + override 構成に移行する — `src/toolchain2/emit/profiles/go.json` のプロファイルに従い、CommonRenderer の共通ノード走査を使う構成にする。Go 固有のノード（FunctionDef のレシーバー、ForCore、multi_return 等）だけ override として残す
   - 完了: `_GoStmtCommonRenderer` / `_GoExprCommonRenderer` 実装済み (commit 5611cc447 等)。`_emit_if` / `_emit_while` dead code を除去（2026-03-30）
2. [x] [ID: P5-CR-GO-S2] fixture 132 件 + sample 18 件の Go compile + run parity を通す
   - 完了: fixture 147 件全 PASS、sample 18 件全 PASS（P1-GO-CONTAINER-S4 で確認済み）

### P0-GO-ENV-TARGET: Go emitter の extern_var インライン置換を修正する

1. [x] [ID: P0-GO-ENV-S1] Go emitter が `extern_var_v1` メタデータ付きの変数参照を、mapping.json の `calls` テーブルから値を取得してインラインリテラルとして出力するよう修正する — 現状は `env` をモジュールとして import しようとして `undefined: env` エラーになる
   - 完了: `mapping.json` に `pytra.std.env` を `skip_modules` 追加、`_emit_attribute` で `owner_id + "." + attr` を `mapping.calls` から直接ルックアップするよう修正
2. [x] [ID: P0-GO-ENV-S2] `pytra_runtime_png` fixture が Go で compile + run parity PASS することを確認する
   - 完了: stdlib/pytra_runtime_png:go PASS（2026-03-30）

### P0-RESOLVE-INT-PROMOTION: BinOp の全演算子で整数昇格 cast がオペランドに付くよう修正する

全ての BinOp（`+`, `-`, `*`, `/`, `//`, `%`, `&`, `|`, `^`, `<<`, `>>`）で、異なるサイズの整数型が混在する場合に、resolve が **演算の前に** 両オペランドを結果型に cast すべき。現状は小さい側を相手のサイズに cast するだけで、結果型への昇格 cast が付かない。Go/Rust は暗黙昇格がないのでコンパイルエラーになる。

例: `m8: int8 = 100; m16: int16 = 100; r5: int32 = m8 * m16`
- NG: `int16(m8) * m16` → 結果は int16（overflow あり）、int32 への cast なし
- OK: `int32(m8) * int32(m16)` → 結果は int32、overflow なし

1. [ ] [ID: P0-RESOLVE-INTPROMO-S1] resolve の BinOp 整数昇格で、全演算子について cast を「結果型にまで昇格」に修正する — 両オペランドに結果型への cast を付ける
2. [ ] [ID: P0-RESOLVE-INTPROMO-S2] `integer_promotion` fixture が Go で compile + run parity PASS することを確認する
3. [ ] [ID: P0-RESOLVE-INTPROMO-S3] 他の fixture に影響がないことを確認する（golden 再生成）

### P2-COMMON-RENDERER-PARENS: CommonRenderer に演算子優先順位ベースの括弧制御を実装する

仕様: [spec-emitter-guide.md](../spec/spec-emitter-guide.md) §1.4

1. [ ] [ID: P2-CR-PARENS-S1] CommonRenderer に演算子優先順位テーブルを受け取る仕組みを追加する — 各言語の emitter が自分の優先順位テーブルを渡す。Go の優先順位テーブルをプロトタイプとして最初に実装する
2. [ ] [ID: P2-CR-PARENS-S2] BinOp / UnaryOp / Compare の出力時に「親の優先順位 ≥ 子の優先順位なら括弧を付ける」ロジックを実装する — 不要な括弧を出力しない
3. [ ] [ID: P2-CR-PARENS-S3] 最外の冗長括弧（`x = (expr);` の外側）を除去する
4. [ ] [ID: P2-CR-PARENS-S4] Go fixture + sample parity に影響がないことを確認する
5. [ ] [ID: P2-CR-PARENS-S5] C++ 担当がC++ の優先順位テーブルを追加し、C++ parity を確認する

### P6-GO-SELFHOST: Go emitter で toolchain2 を Go に変換し go build を通す

前提: P1-GO-CONTAINER-WRAPPER 完了後に着手。

1. [ ] [ID: P6-GO-SELFHOST-S0] selfhost 対象コード（`src/toolchain2/` 全 .py）で戻り値型の注釈が欠けている関数に型注釈を追加する — resolve が `inference_failure` にならない状態にする
2. [ ] [ID: P6-GO-SELFHOST-S1] toolchain2 全 .py を Go に emit し、go build が通ることを確認する
3. [ ] [ID: P6-GO-SELFHOST-S2] go build 失敗ケースを emitter/runtime の修正で解消する（EAST の workaround 禁止）
4. [ ] [ID: P6-GO-SELFHOST-S3] selfhost 用 Go golden を配置し、回帰テストとして維持する
