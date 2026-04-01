# P0-CPP-OPT-VARIANT: optional<variant> 移行後の C++ parity 回復

最終更新: 2026-04-02

## 背景

C++ emitter で `T1 | T2 | None` の型写像を `std::variant<..., std::monostate>` から `std::optional<std::variant<...>>` に変更した（commit f8c4c618b）。

これにより EAST の `OptionalType(inner=UnionType)` → C++ `std::optional<std::variant<...>>` が Rust の `Option<enum>` と対応し、`is None` チェックが `py_is_none()` / `has_value()` で統一された。

移行後の parity 状況:
- fixture: 130/137 PASS（変更前と同数、回帰なし）
- sample: 18/18 PASS
- stdlib 非JSON: 13/13 PASS
- stdlib JSON: 0/3 FAIL（`json_extended`, `json_indent_optional`, `json_nested`）

JSON 3件の FAIL は、JsonValue の `resolved_type` が `bool | int64 | float64 | str | ... | None` に展開され、`list[JsonValue]` が `list<optional<variant<...>>>` になることで関数シグネチャが不一致になるのが原因。JsonValue は `NominalAdtType` として扱われるべきで、resolved_type 文字列の展開が根本原因。

## 対象

- `src/toolchain2/emit/cpp/emitter.py` — optional<variant> 周りの emit 補正
- `src/toolchain2/emit/cpp/types.py` — NominalAdtType / JsonValue の型写像
- `src/runtime/cpp/` — optional<variant> 用の runtime helper 追加が必要であれば
- `test/stdlib/source/py/` — json_extended, json_indent_optional, json_nested

## 非対象

- Rust emitter の enum 化（別タスク）
- fixture 130→137 の残り 7 件（既存の別原因 failure）

## 受け入れ基準

- [ ] `json_extended` が C++ stdlib parity で PASS する
- [ ] `json_indent_optional` が C++ stdlib parity で PASS する
- [ ] `json_nested` が C++ stdlib parity で PASS する
- [ ] fixture 130/137、sample 18/18 に回帰がない

## サブタスク

1. [ ] [ID: P0-CPP-OPT-VAR-S1] JsonValue の resolved_type 展開が optional<variant> に巻き込まれる原因を調査し、NominalAdtType の型写像を修正する
2. [ ] [ID: P0-CPP-OPT-VAR-S2] json_extended / json_indent_optional / json_nested が C++ parity PASS することを確認する
3. [ ] [ID: P0-CPP-OPT-VAR-S3] fixture + sample に回帰がないことを確認する

## 決定ログ

- 2026-04-01: monostate → optional<variant> 移行を実施。fixture/sample/stdlib(非JSON) は回帰なし。JSON 3件は NominalAdtType の resolved_type 展開が根本原因として起票。
