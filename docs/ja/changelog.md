# 更新履歴

## 2026-03-26

- **パイプライン再設計完了**: parse → resolve → compile → optimize → link → emit の 6 段パイプライン（`pytra-cli2`）が全段動作。toolchain2 は toolchain に一切依存しない独立実装。
- **Go backend 新パイプライン移行**: Go emitter + runtime を新パイプラインで実装。sample 18/18 emit 成功。旧 Go emitter/runtime を削除。
- **C++ emitter 新規実装**: `toolchain2/emit/cpp/` に新パイプライン用 C++ emitter を実装。fixture 132/132, sample 18/18 emit 成功。
- **CodeEmitter 基底クラス**: `mapping.json` による runtime_call 写像を全 emitter で共有。ハードコード除去。
- **仕様整合 (Codex-review)**: resolve/parser/validator/linker/emitter の仕様違反 20 件以上を修正。
- **spec-east1.md / spec-east2.md**: EAST1（型未解決）と EAST2（型確定）の出力契約を正式定義。
- **spec-builtin-functions.md**: built-in 関数の宣言仕様。POD/Obj 型分類、dunder 委譲、extern_fn/extern_var/extern_class/extern_method。
- **spec-runtime-mapping.md**: mapping.json のフォーマット仕様。implicit_promotions テーブル。
- **integer promotion**: C++ usual arithmetic conversion に準拠した数値昇格 cast を resolve で挿入。
- **bytearray 対応**: `pytra/utils/png.py` / `gif.py` を `list[int]` → `bytearray` に書き換え。Go で `[]byte` に写像。

## 2026-03-25

- **P0 全完了**: parse/resolve/compile/optimize/link/emit の全段が golden file テストと一致。
- **test/ ディレクトリ再編**: fixture/sample/include/pytra/selfhost の 5 カテゴリに整理。
- **golden file 自動再生成**: `tools/regenerate_golden.py` で全段 golden を一括再生成。
- **Go emitter**: お手本 emitter として実装。fixture 132/132, sample 18/18 emit 成功。
- **Go runtime + parity**: sample 18/18 で `go run` + stdout 一致。Go は Python の 63x 高速。
- **Go runtime 分解**: `pytra_runtime.go` 全部入り → `built_in/` + `std/` + `utils/` に分離。

## 2026-03-24

- **パイプライン再設計着手**: parse/resolve/compile/optimize/emit の 5 段（後に link 追加で 6 段）パイプラインを設計。
- **toolchain2/ 新規作成**: 現行 toolchain/ とは独立した新パイプライン実装。selfhost 対象（Any/object 禁止、pytra.std のみ）。
- **pytra-cli2**: 新 CLI。-parse/-resolve/-compile/-optimize/-link/-emit/-build サブコマンド。
- **EAST1 golden file**: spec-east1 準拠で golden を strip（型情報除去）。150 件。
- **built-in 関数宣言**: `src/include/py/pytra/built_in/builtins.py` + `containers.py`。v2 extern（extern_fn/extern_var/extern_class/extern_method）。
- **stdlib 宣言**: `src/include/py/pytra/std/` に math/time/glob/os/sys 等の v2 extern 宣言。

## 2026-03-20 | v0.15.0

- backend として PowerShell をサポート。

## 2026-03-18 | v0.14.0

- 再帰的 union type をサポート。

## 2026-03-11 | v0.13.0

- NES(ファミコン)のエミュレーターを Python + SDL3 で作成。C++ に変換できるよう Pytra 側を改良中。

## 2026-03-10 | v0.12.0

- Runtime 整理の大工事中。

## 2026-03-09 | v0.11.0

- object 境界を見直し中。チュートリアルを整備。

## 2026-03-08 | v0.10.0

- `@template` を使えるようになった。各言語の runtime を整備中。

## 2026-03-07 | v0.9.0

- 大規模リファクタリング完了。全言語で再び使えるようになった。`@extern` と `@abi` を使えるようになり、変換後のコードを他言語からも呼び出せるようになった。

## 2026-03-06 | v0.8.0

- ABI 境界を定義しなおして大規模リファクタリング実施中。(C++ 変換器以外は一時的に壊れていた)

## 2026-03-04 | v0.7.0

- 変換対象として PHP を追加。Nim 正式対応作業中。

## 2026-03-02 | v0.6.0

- 変換対象として Scala を追加。

## 2026-03-01 | v0.5.0

- 変換対象として Lua を追加。

## 2026-02-28 | v0.4.0

- 変換対象として Ruby を追加。

## 2026-02-27 | v0.3.0

- EAST（中間表現）を段階処理（EAST1→EAST2→EAST3）へ整理。C++ CodeEmitter の大規模分割・縮退。

## 2026-02-25 | v0.2.0

- 全言語について元ソースコードに近い形で出力されるようになった。

## 2026-02-23 | v0.1.0

- Python の元ソースコードに極めて近いスタイルで、読みやすい C++ コードを生成できるようになった。
