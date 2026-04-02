# P0-SUBSCRIPT-BOUNDS: negative-index-mode / bounds-check-mode を EAST optimizer に移管する

最終更新: 2026-04-02

## 背景

旧 toolchain の emitter に `--negative-index-mode`（`always` / `const_only` / `off`）と `--bounds-check-mode`（`always` / `debug` / `off`）があった。旧デフォルトは `const_only` + `off`。

toolchain2 ではこのオプションが移行されておらず、C++ runtime の `py_list_at_ref` が全 `Subscript` アクセスで常に負数正規化 + bounds check を行っている。1600x1200 PNG 書き出しで数百万回の hot loop indexing が遅い直接原因。

### 設計上の問題

旧 toolchain ではこのオプションが **emitter のオプション** だった。これは設計として正しくない:
- emitter はオプションの存在を知るべきではない
- 最適化判断は EAST optimizer の責務
- emitter は EAST3 のメタデータを写像するだけ

## 方針

### `--east3-opt-level` を `--opt-level` に改名し、最適化プリセットとして統合する

旧 `--east3-opt-level` は内部実装名がそのまま CLI に露出している。ユーザーから見れば単に「最適化レベル」なので `--opt-level` に改名する。

`--opt-level` がデフォルトの `negative_index_mode` / `bounds_check_mode` を決定し、個別オプションで上書きできる:

| `--opt-level` | 意味 | `negative_index_mode` デフォルト | `bounds_check_mode` デフォルト |
|---|---|---|---|
| `0` | 最適化なし、Python 完全互換 | `always` | `always` |
| `1` | 軽量最適化（デフォルト） | `const_only` | `off` |
| `2` | 積極最適化 | `off` | `off` |

個別オプション（`--negative-index-mode` / `--bounds-check-mode`）は `--opt-level` のデフォルトを上書きする:
```
--opt-level 2 --negative-index-mode always   # 積極最適化だが負数インデックスは常に正規化
```

### Python の添字セマンティクスと negative_index / bounds_check の連動

Python の `a[i]` は以下のステップで動作する:

```python
if i < 0:
    i += len(a)        # ← negative_index（正規化）
if i < 0 or i >= len(a):
    raise IndexError   # ← bounds_check（範囲チェック）
```

**negative_index と bounds_check は独立ではなく連動する。** `a[-100]` は正規化後もまだ負なので IndexError になる。正規化なしで bounds check だけ入れると、負数は即 IndexError（Python と挙動が変わる）。

| | bounds_check on | bounds_check off |
|---|---|---|
| **negative_index on** | Python 完全互換 | 正規化するが範囲外は未定義 |
| **negative_index off** | 負数は即エラー（正規化しない） | 全て未定義（最速） |

**リテラル負数（`a[-1]`）の扱い:**
- `negative_index: off` では `a[-1]` も正規化しない。C++ なら `vector[-1]` で未定義動作。これはユーザーの選択
- リテラル負数だけ特別扱いすると `off` の意味が一貫しない
- `off` は本当に off。`a[-1]` を使うコードは `--opt-level 2` では壊れる。`--opt-level 1`（デフォルト）では `const_only` なのでリテラル負数は正規化される

### EAST lowering / optimizer / emitter の責務

添字の処理は **EAST2 → EAST3 lowering** と **optimizer** の 2 段で行う:

**EAST2 → EAST3 lowering（負数リテラルの静的展開）:**
- `negative_index_mode=always` / `const_only`: リテラル負数 `a[-1]` を `a[len(a) - 1]` に展開
- `negative_index_mode=off`: リテラル負数もそのまま残す（emitter にそのまま渡る）
- 変数インデックスは lowering では触らない（静的に負かどうか判定できない）

**optimizer（メタデータ付与）:**
- `Subscript` ノードに `meta.subscript_access_v1` を付与する:
  - `negative_index: "normalize" | "skip"` — 実行時の負数正規化（`if (i < 0) i += len`）の要否
  - `bounds_check: "full" | "off"` — 範囲チェックの要否
- 判定ロジック:
  - `ForRange` ループ変数による添字 → `negative_index: "skip"`, `bounds_check: "off"`（常に安全）
  - lowering 済みリテラル（非負確定）→ `negative_index: "skip"`
  - 負数リテラル → `negative_index: "normalize"`, `bounds_check: "full"`（正規化後も範囲外になり得るため fail-closed）
  - 変数インデックス → `negative_index_mode` 設定に従う
  - `bounds_check` → `bounds_check_mode` 設定に従う

**emitter:**
- メタデータを見て runtime API を選ぶだけ:
  - `bounds_check: "full"` + `negative_index: "normalize"` → `py_list_at_ref`（既存、full check）
  - `bounds_check: "off"` + `negative_index: "skip"` → 直接 `operator[]` / ネイティブ添字
  - `bounds_check: "full"` + `negative_index: "skip"` → bounds check のみ、正規化なし
  - `bounds_check: "off"` + `negative_index: "normalize"` → 正規化のみ、bounds check なし
- emitter は `--opt-level` / `--negative-index-mode` / `--bounds-check-mode` のオプション自体を知らない

## 対象

- `src/toolchain2/optimize/` — optimizer にオプションとメタデータ付与ロジックを追加
- `docs/ja/spec/spec-east.md` — `meta.subscript_access_v1` スキーマ定義
- `docs/ja/spec/spec-east3-optimizer.md` — optimizer パス仕様に追記
- `src/toolchain2/emit/cpp/emitter.py` — メタデータに基づく API 選択（emitter はオプションを知らない）
- 全 emitter — 同上

## 非対象

- emitter にオプションを生やすこと（禁止）
- `src/pytra/utils/png.py` の正本改善（別タスク、ただし相乗効果あり）

## 既存ドキュメントの状況

- `docs/en/spec/spec-options.md` に旧 emitter オプションとして `--negative-index-mode` / `--bounds-check-mode` / `-O0`~`-O3` が記載されている
- `docs/ja/spec/archive/20260328-spec-options.md` に日本語版（archive 済み）
- いずれも「emitter のオプション」として書かれており、EAST optimizer のオプションとしての記述はない
- `docs/ja/tutorial/transpiler-cli.md` にも `--bounds-check-mode` が emitter CLI オプションとして記載
- `docs/ja/tutorial/advanced-usage.md` に `-O3` が記載
- toolchain2 にはこれらが一切移行されていない
- spec-east.md / spec-east3-optimizer.md にも該当記述なし

## 受け入れ基準

- [ ] `--east3-opt-level` が `--opt-level` に改名されている
- [ ] `--opt-level` が `negative_index_mode` / `bounds_check_mode` のデフォルトを決定する
- [ ] `--negative-index-mode` / `--bounds-check-mode` で個別上書きできる
- [ ] `Subscript` ノードに `meta.subscript_access_v1` が付与される
- [ ] emitter はメタデータのみを参照し、オプション自体を知らない
- [ ] C++ sample 01 (mandelbrot) の実行時間が Rust/Go と同等レベルに改善される
- [ ] fixture + sample parity に回帰がない
- [ ] spec-options.md を更新し、EAST optimizer のオプションとして再定義する（emitter オプションの記述を削除）
- [ ] spec-east3-optimizer.md に `subscript_access_v1` パスを追記する
- [ ] `docs/ja/tutorial/transpiler-cli.md` のオプション欄を更新する（emitter オプションではなく EAST optimizer オプションとして記述）
- [ ] `docs/ja/tutorial/advanced-usage.md` の `-O3` 記述を更新する

## サブタスク

1. [x] [ID: P0-SUB-BOUNDS-S1] `meta.subscript_access_v1` スキーマを spec-east.md に定義する
2. [ ] [ID: P0-SUB-BOUNDS-S1.5] `--east3-opt-level` を `--opt-level` に改名する（pytra-cli2.py, runtime_parity_check_fast.py, optimizer, spec, tutorial 全箇所）
3. [ ] [ID: P0-SUB-BOUNDS-S2] optimizer に `--opt-level` と `--negative-index-mode` / `--bounds-check-mode` の連動を実装する
   - `--opt-level` がデフォルトの `negative_index_mode` / `bounds_check_mode` を決定する
   - `--negative-index-mode` / `--bounds-check-mode` で個別上書きできる
   - `optimize_east3_document()` の引数に `negative_index_mode` / `bounds_check_mode` を追加する
   - `runtime_parity_check_fast.py` にも `--opt-level` / `--negative-index-mode` / `--bounds-check-mode` を追加して optimizer に引き回す
4. [ ] [ID: P0-SUB-BOUNDS-S3] C++ emitter でメタデータに基づく direct index / py_list_at_ref の分岐を実装する
5. [ ] [ID: P0-SUB-BOUNDS-S4] sample 01 (mandelbrot) の C++ 実行時間が改善されることを確認する
6. [ ] [ID: P0-SUB-BOUNDS-S5] fixture + sample + stdlib parity に回帰がないことを確認する
7. [ ] [ID: P0-SUB-BOUNDS-S6] negative index の回帰 fixture を追加する — `a[-1]` / `a[-2]` を含む fixture で、optimizer が誤って `negative_index: skip` を付けた場合に FAIL になることを検証する

## 決定ログ

- 2026-04-02: C++ sample 01 が Python と同等（12.8s vs 34.9s、Rust 1.9s）と遅い原因を調査。PNG runtime の `py_list_at_ref` が毎回 bounds check + 負数正規化していることが根本原因。旧 toolchain では `bounds_check_mode=off` がデフォルトだったが toolchain2 に未移行。emitter のオプションではなく EAST optimizer の責務として再設計する方針で起票。
- 2026-04-02: `--east3-opt-level` は内部実装名がそのまま CLI に露出しているので `--opt-level` に改名する。`--opt-level` が `negative_index_mode` / `bounds_check_mode` のデフォルトを決定し、個別オプションで上書きできる設計にする。
