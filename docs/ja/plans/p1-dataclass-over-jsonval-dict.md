# P1-DATACLASS-OVER-JSONVAL-DICT: 一時構造体の dict[str, JsonVal] を @dataclass に置き換える

最終更新: 2026-04-25

## 背景

toolchain のコード（parse/resolve/compile/link）で、一時的なデータ受け渡しに `dict[str, JsonVal]` を多用している。これは Python では動くが、selfhost（C++ 変換）で以下の問題を引き起こす。

1. **型情報の喪失** — フィールドが `JsonVal` に埋もれ、EAST の型推論が効かない。ループ変数や get の戻り値が `unknown` になる
2. **null-only 構造の脆弱性** — 全フィールドが None の dict を C++ に変換すると `Optional<int>` や `std::nullopt` の扱いで壊れやすい
3. **共変性の暗黙依存** — `list[dict[str, JsonVal]]` を `list[JsonVal]` に入れるパターンが C++ の型チェックで弾かれる（type_norm.py / type_resolver.py で実際に発生）
4. **可読性** — `span["lineno"]` より `span.lineno` のほうが意図が明確

## 方針

- EAST ノードの走査で受け取る入力型としての `dict[str, JsonVal]` は正しい用途であり、変更しない
- toolchain 内部でデータを受け渡すために**新規作成**している `dict[str, JsonVal]` を `@dataclass` に置き換える
- 対象は emitter の手前の段（parse/resolve/compile/link）を優先する
- emitter 側は emitter-guide §1.3 で新規利用を禁止済み。既存コードは selfhost blocker に当たったものから順次移行

## 対象範囲と作業量の概算

| 層 | `dict[str, JsonVal]` 出現数 | うち入力型（走査用） | うち一時構造体（置換対象） |
|---|---|---|---|
| parse | ~139 | 多数（nodes.py の to_jv 等） | source_span, nodes の一部 |
| resolve | ~172 | 多数（resolver の EAST ノード操作） | builtin_registry の型情報、resolver 内部の中間結果 |
| compile | ~46 | 多数（lower のノード走査） | type_summary の型情報 |
| link | ~227 | 多数（linker のノード走査） | shared_types, manifest 構造 |

正確な置換対象数は各ファイルを精査して決める（S1 で実施）。

## サブタスク

### S1: 棚卸しと優先順位付け

selfhost build で実際にブロッカーになった/なりそうな箇所を洗い出し、優先順位を付ける。
既知の例:
- `SourceSpan` の null-only dict（対処済み）
- `type_norm.py` / `type_resolver.py` の `list[dict[str, JsonVal]]` vs `list[JsonVal]`（対処済み）
- `builtin_registry.py` の型情報構造

### S2: parse 層の @dataclass 化

`src/toolchain/parse/py/` 配下の一時構造体を `@dataclass` に置き換える。
`nodes.py` は既に `@dataclass` を使っているが、`to_jv()` の内部で `dict[str, JsonVal]` を返す経路が残っている。

### S3: resolve 層の @dataclass 化

`src/toolchain/resolve/py/` 配下。`resolver.py` (153箇所) が最大だが、大部分は EAST ノード走査の入力型。内部の中間結果構造を `@dataclass` に切り替える。

### S4: compile 層の @dataclass 化

`src/toolchain/compile/` 配下。`type_summary.py` (20箇所) の型情報構造が主な対象。

### S5: link 層の @dataclass 化

`src/toolchain/link/` 配下。`linker.py` (133箇所) が最大だが、走査用が大半。`shared_types.py`, `type_stubgen.py` の内部構造が対象。

## 非対象

- EAST ノードの走査で受け取る入力型としての `dict[str, JsonVal]` — これは JSON 由来の EAST データの表現であり、変更しない
- emitter 層 — emitter-guide §1.3 で新規禁止済み。既存の移行は各 backend 担当の selfhost 作業で漸進的に実施
- `to_jv()` の戻り値型変更 — EAST の JSON シリアライズ契約に関わるため、別タスクで判断

## 制約

- `@dataclass` は selfhost 対象コードで使用可能（`from dataclasses import dataclass` は no-op import として許可済み）
- 新規 `@dataclass` は `src/toolchain/` 配下の適切なモジュールに配置する
- 既存のテストや golden が壊れないよう、外部 API（EAST JSON 出力）は変えない

## 決定ログ

- 2026-04-25: 起票。selfhost の null-only dict / covariance 系ブロッカーの根本対策として、一時構造体の `@dataclass` 化を進める方針を決定。emitter-guide §1.3 に新規利用禁止ルールを追加済み。
