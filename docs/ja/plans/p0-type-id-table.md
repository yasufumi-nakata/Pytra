# P0-TYPE-ID-TABLE: linker による type_id テーブル仮想モジュール生成

最終更新: 2026-03-28
ステータス: 完了

## 背景

現在 C++ runtime は `g_type_table[4096]` というハードコード固定サイズ配列を持ち、Go runtime は `PYTRA_TID_VALUE_ERROR = 12` 等の手書き定数を持っている。linker が type_id を確定しているにもかかわらず、その値を runtime に渡す仕組みがないため、「たまたま番号が一致しているから動いている」状態。

spec-type_id.md §7 で設計した `pytra.built_in.type_id_table` 仮想モジュールを linker が生成し、emitter が通常の EAST3 として写像することで、全言語で type_id テーブルのハードコードを撤廃する。

## サブタスク

1. [ID: P0-TID-TABLE-S1] `pytra/built_in/` に `pytra_isinstance(actual_type_id: int, tid: int) -> bool` を pure Python で定義する — `id_table[tid * 2] <= actual_type_id <= id_table[tid * 2 + 1]` の判定関数
2. [ID: P0-TID-TABLE-S2] linker に `pytra.built_in.type_id_table` 仮想モジュール生成を実装する — `id_table: list[int]` と型ごとの TID 定数（`VALUE_ERROR_TID: int = 3` 等）を EAST3 として生成し link-output に含める
3. [ID: P0-TID-TABLE-S3] linker が isinstance を `pytra_isinstance(x.type_id, TID定数)` に lower する際、対象モジュールの `meta.import_bindings` に `pytra.built_in.type_id_table` からの import を挿入する
4. [ID: P0-TID-TABLE-S4] C++ runtime の `g_type_table[4096]` ハードコードを撤廃し、linker 生成の `pytra.built_in.type_id_table` を使う形に移行する
5. [ID: P0-TID-TABLE-S5] Go runtime の手書き TID 定数（`PYTRA_TID_VALUE_ERROR = 12` 等）を撤廃し、linker 生成のモジュールを使う形に移行する
6. [ID: P0-TID-TABLE-S6] fixture + sample の C++/Go parity 確認

## 受け入れ基準

1. `pytra.built_in.type_id_table` が linker の link-output に含まれること
2. isinstance が `pytra_isinstance(x.type_id, VALUE_ERROR_TID)` の形で生成コードに出力されること
3. C++ runtime にハードコード固定サイズ配列（`g_type_table[4096]`）が存在しないこと
4. Go runtime に手書き TID 定数が存在しないこと
5. 既存 fixture + sample の C++/Go parity が維持されること

## 決定ログ

- 2026-03-28: C++ runtime のコードレビューで `g_type_table[4096]` のハードコードが発覚。Go も手書き定数。linker が type_id を確定しているのに runtime に渡す仕組みがない問題を特定。
- 2026-03-28: linker が `pytra.built_in.type_id_table` を仮想モジュールとして生成し、`id_table: list[int]` + TID 定数を EAST3 に載せる方式を設計。emitter は通常の EAST3 として写像するだけ。
- 2026-03-28: isinstance の判定は `pytra_isinstance(actual_type_id, tid)` の1引数形式。`id_table[tid * 2]` で min、`id_table[tid * 2 + 1]` で max を引く。
- 2026-03-28: `id_table` / TID 定数の helper 生成は `build_type_id_table()` の結果のみを正本とし、linker 内の min/max ハードコード案は撤回。
- 2026-03-28: Go backend は `pytra.built_in.type_id_table` だけを emit し、`pytra_isinstance` 本体は `py_runtime.go` の helper として参照させる形で parity を維持。
