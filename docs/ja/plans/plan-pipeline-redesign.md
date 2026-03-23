# パイプライン再設計案: parse / resolve / compile / optimize / emit 五段分離

最終更新: 2026-03-24
ステータス: 案（検討中）

## 1. 動機

現行パイプラインには以下の構造的問題がある。

1. **signature_registry のハードコード**: `pytra/std/*.py` の関数シグネチャを正規表現パースしてキャッシュし、型推論に注入している。stdlib が増えるたびに手動メンテナンスが必要。
2. **built-in 型のハードコード**: `len` → `int64`、`str` → `str` 等の組み込み関数の型情報がパーサー内部にハードコードされている。
3. **cross-module 型解決の設計矛盾**: EAST1→EAST2→EAST3 はモジュール単位の独立処理だが、EAST2 の型推論で他モジュールの関数シグネチャが必要。モジュール独立なのに cross-module 情報が要るという矛盾を、ハードコードテーブルで糊塗している。
4. **EAST1 の言語固有性が不明確**: EAST1 は Python パーサーの出力だが、ファイル名や段の構成からそれが読み取れない。将来の多言語 frontend 対応で混乱する。

## 2. 提案: parse / resolve / compile / optimize / emit 五段パイプライン

### 2.1 概要

```
parse:     .py → .py.east1          言語固有の構文解析（モジュール単位・完全並列）
resolve:   *.py.east1 → *.east2    型解決 + 正規化（全モジュール一括・依存順）
compile:   *.east2 → *.east3       core lowering（言語非依存）
optimize:  *.east3 → *.east3       whole-program 最適化
emit:      *.east3 → *.cpp 等      target コード生成（写像のみ）
```

通常使用は `-build` で一括実行:

```
pytra-cli2 -build --target=cpp a.py   （parse→resolve→compile→optimize→emit を一気通貫）
```

### 2.2 各段の責務

#### parse（言語固有・モジュール単位）

```
pytra-cli2 -parse a.py        →  a.py.east1
pytra-cli2 -parse math.py     →  math.py.east1
```

- 入力: ソースファイル 1 つ
- 出力: `.py.east1`（Python 固有の EAST1）
- 責務: 構文解析、ソース span / trivia 保持、型注釈の保持（未解決）
- cross-module 依存: **なし**（完全にモジュール独立）
- 並列性: **完全並列**
- 実装: `toolchain2/parse/py/`

#### resolve（言語固有→言語非依存・全モジュール一括）

```
pytra-cli2 -resolve --from=python *.py.east1  →  *.east2
```

- 入力: 全 `.py.east1`（built-in + stdlib + ユーザーコード）
- 出力: `.east2`（言語非依存の正規化済み IR）
- 責務:
  - import graph のトポロジカルソート
  - 依存順に各モジュールの型解決（先行モジュールのシグネチャを参照）
  - Python 固有の構文正規化（`range()` → `ForRange`、`int` → `int64` 等）
  - cast 挿入（`int64` → `float64` 等）
  - `--from=python` で入力言語の正規化ルールを指定
- cross-module 依存: **あり**（全モジュールが揃っている前提）
- 並列性: 内部で依存順に処理（DAG 内の独立ノードは並列可能）
- 実装: `toolchain2/resolve/py/`

#### compile（言語非依存・core lowering）

```
pytra-cli2 -compile *.east2  →  *.east3
```

- 入力: 全 `.east2`
- 出力: `.east3`（core IR）
- 責務:
  - boxing/unboxing 命令化
  - `type_id` 判定・反復計画の命令化
  - `dispatch_mode` の意味適用
  - 現行の EAST2→EAST3 lowering に相当
- cross-module 依存: **あり**
- 実装: `toolchain2/compile/`

#### optimize（言語非依存・whole-program 最適化）

```
pytra-cli2 -optimize *.east3  →  *.east3
```

- 入力: 全 `.east3`
- 出力: 最適化済み `.east3`
- 責務:
  - whole-program 解析（call graph、escape 解析、container ownership）
  - dead code 除去
  - 現行の linker optimizer に相当
- cross-module 依存: **あり**
- 実装: `toolchain2/optimize/`

#### emit（言語非依存→target・全モジュール一括）

```
pytra-cli2 -emit --target=cpp *.east3  →  *.cpp
pytra-cli2 -emit --target=rs  *.east3  →  *.rs
```

- 入力: 全 `.east3`
- 出力: target 言語のソースファイル群
- 責務:
  - EAST3 ノードから target 言語構文への写像（**のみ**）
  - runtime 配置・include / import 生成
  - 最適化はしない
- cross-module 依存: **あり**（import / include の解決）
- 実装: `toolchain2/emit/cpp/` 等

### 2.3 一括実行コマンド

```
# 通常使用: parse→resolve→compile→optimize→emit を一括
pytra-cli2 -build --target=cpp a.py
```

`-build` は中間ファイルを一時ディレクトリに生成し、最終出力のみを残す。個別コマンドはパイプラインの途中を覗きたいとき用。

### 2.4 ファイル命名規則

| ファイル | 意味 |
|---|---|
| `a.py` | Python ソース |
| `a.py.east1` | Python 固有の EAST1（パーサー出力） |
| `a.east2` | 言語非依存の EAST2（`.py` が消える = 言語固有の意味論が除去された） |
| `a.east3` | 最適化済みの EAST3 |

`.py.east1` → `.east2` で拡張子から `.py` が消えることが、「Python の意味論が抜けた」ことを自己説明する。

### 2.5 built-in / stdlib の統一的扱い

built-in も stdlib もユーザーコードと同じ仕組みで処理する。

```
pytra-cli2 -parse pytra/built_in.py       →  built_in.py.east1
pytra-cli2 -parse pytra/std/math.py       →  math.py.east1
pytra-cli2 -parse pytra/std/json.py       →  json.py.east1
pytra-cli2 -parse user_code.py            →  user_code.py.east1

pytra-cli2 -resolve --from=python *.py.east1  →  *.east2

pytra-cli2 -compile *.east2  →  *.east3

pytra-cli2 -optimize *.east3  →  *.east3

pytra-cli2 -emit --target=cpp *.east3  →  *.cpp
```

- `built_in.py` には `len`, `str`, `int`, `print` 等の関数宣言を記述
- `pytra/std/*.py` には stdlib の関数宣言を記述（現行と同じ）
- resolve 段が `built_in.py.east1` の `FunctionDef` ノードから戻り値型を取得
- **signature_registry のハードコードテーブルは全て不要になる**
- **built-in 型のパーサー内ハードコードも全て不要になる**
- built-in や stdlib の追加・変更は `.py` ファイルの編集のみで対応可能

## 3. 現行との対応

| 提案 | 現行の実装 | 変更点 |
|---|---|---|
| parse | `core.py` + EAST1 ビルド | CLI の分離。実装はほぼ流用可。 |
| resolve | `east2.py` + signature_registry + built-in ハードコード | signature_registry 除去。built-in ハードコード除去。cross-module 型解決を追加。 |
| compile | `east2_to_east3_lowering.py` | core lowering のみに限定。 |
| optimize | linker optimizer | whole-program 最適化のみに限定。 |
| emit | emitter 群 | 最適化責務を除去し、写像のみに限定。 |

### 3.1 現行 EAST 段との対応

| 現行 | 提案での位置 |
|---|---|
| EAST1 | parse の出力（`.py.east1`） |
| EAST2 | resolve の出力（`.east2`） |
| EAST3 | compile の出力（`.east3`） / optimize の入出力 |

EAST1 / EAST2 / EAST3 のノード定義は変更不要。実行タイミングとデータの流れが変わるのみ。

### 3.2 ディレクトリ構成

```
src/
  pytra-cli2.py               ← 新 CLI
  pytra/                      ← 共有（std, utils, built_in）
  toolchain/                  ← 現行（触らない）
  toolchain2/
    parse/py/                 ← Python → .py.east1（言語固有）
    resolve/py/               ← .py.east1 → .east2（言語固有の正規化 + cross-module 型解決）
    compile/                  ← .east2 → .east3（言語非依存の core lowering）
    optimize/                 ← .east3 → 最適化済み .east3（whole-program）
    emit/
      cpp/                    ← .east3 → .cpp（target 固有）
      rs/
      ...
```

### 3.3 テストディレクトリ構成

各段の出力を golden file として検証する。パイプラインの各段を独立にテストでき、どの段でリグレッションが起きたか特定しやすい。

```
test/
  east1/py/      ← .py → .py.east1 のスナップショットテスト（Python 固有）
  east2/py/      ← .py.east1 → .east2 のスナップショットテスト（入力が Python 由来）
  east3/         ← .east2 → .east3 のスナップショットテスト（言語非依存）
  east3-opt/     ← optimize 後の .east3 のスナップショットテスト（言語非依存）
  emit/
    cpp/         ← .east3 → .cpp の golden file テスト（target 固有）
    rs/
    ...
```

- `east1/py/`, `east2/py/` は入力言語ごとにサブディレクトリを持つ（将来 `east1/rb/` 等に対応）
- `east3/`, `east3-opt/` は言語非依存なのでサブディレクトリなし
- `emit/cpp/` 等は target 言語ごとにサブディレクトリを持つ
- `toolchain2/` と `test/` の構造が対称になる

## 4. 除去されるもの

- `src/toolchain/frontends/signature_registry.py` のハードコードテーブル全体
- `src/toolchain/frontends/frontend_semantics.py` のハードコードテーブル（semantic_tag 等）
- `core_expr_named_call_annotation.py` 等の built-in 型ハードコード
- `_NONCPP_MODULE_ATTR_RUNTIME_CALLS` 等の runtime dispatch テーブル

## 5. 移行方針

（未定。段階的に移行するか、一括で切り替えるかを検討する。）

## 6. 未決事項

- `--from=python` 以外の frontend が現実的に必要になる時期
- `.east1` / `.east2` / `.east3` のシリアライズ形式（JSON 維持 or バイナリ形式導入）
- optimize 段をスキップするオプション（`-build --no-optimize` 等）の提供
- `-build` 時の中間ファイル配置（一時ディレクトリ or `work/` 配下）
