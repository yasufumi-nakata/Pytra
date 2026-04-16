# P1-EMITTER-SELFHOST-PER-BACKEND: 各 backend emitter の単独 selfhost

最終更新: 2026-04-16

## 背景

現状、selfhost の作業は `src/pytra-cli.py` をエントリにして「トランスパイラ全体」を C++ に変換する方針で進んでいる。この経路は 31 モジュール（parse/resolve/compile/link/optimize + CLI）を引き込むため、parse/resolve 層の source 型注釈不整合で blocker が頻発しており、emitter 本体の selfhost 化まで到達できていない。

一方、pytra の backend emitter はすべて subprocess で独立起動する設計になっている:

```
pytra-cli.py → EAST3 + manifest.json
                    ↓
    python3 -m toolchain.emit.<lang>.cli manifest --output-dir ...
```

各 emitter は manifest.json を読んで target 言語のソースを吐くだけの自己完結プログラムで、他言語の emitter を import していない。例えば C++ emitter を単独で辿ると依存は 16 モジュールに収まり、parse/resolve 層は含まれない。

## 目的

- 各 backend 担当が、自分の `toolchain.emit.<lang>.cli` をエントリに selfhost C++ build を通す
- parse/resolve 層の selfhost ブロッカーから切り離し、各 backend が並行して進められる状態にする
- 将来の「全体 selfhost」に向けて、emitter 層を先行して selfhost-safe にしておく

## 対象 backend と担当 TODO

| backend | emitter entry | TODO ファイル |
|---|---|---|
| cpp | `toolchain.emit.cpp.cli` | cpp.md |
| cs | `toolchain.emit.cs.cli` | cs.md |
| dart | `toolchain.emit.dart.cli` | dart.md |
| go | `toolchain.emit.go.cli` | go.md |
| java | `toolchain.emit.java.cli` | java.md |
| julia | `toolchain.emit.julia.cli` | julia.md |
| kotlin | `toolchain.emit.kotlin.cli` | java.md（JVM 共通） |
| lua | `toolchain.emit.lua.cli` | lua.md |
| nim | `toolchain.emit.nim.cli` | nim.md |
| php | `toolchain.emit.php.cli` | php.md |
| powershell | `toolchain.emit.powershell.cli` | powershell.md |
| ruby | `toolchain.emit.ruby.cli` | ruby.md |
| rust | `toolchain.emit.rs.cli` | rust.md |
| scala | `toolchain.emit.scala.cli` | java.md（JVM 共通） |
| swift | `toolchain.emit.swift.cli` | swift.md |
| ts (含 js) | `toolchain.emit.ts.cli` | ts.md |
| zig | `toolchain.emit.zig.cli` | zig.md |

## 共通サブタスク（各 backend で S1〜S3 を繰り返す）

### S1: emitter 単独 selfhost build を試行する

`python3 src/pytra-cli.py -build src/toolchain/emit/<lang>/cli.py --target cpp -o work/selfhost/emit/<lang>/` で C++ に変換。parse/resolve/lowering/optimize/link を通過することを確認する。

### S2: C++ コンパイル（g++）を通す

生成された C++ ソースを `g++ -std=c++20 -O0` でコンパイル。型不整合・未定義参照等の blocker を潰す。blocker の多くは **source 側の型注釈不足・不整合** になる想定（今まで出た例: `list[dict[str, JsonVal]]` vs `list[JsonVal]` 混同、戻り値型注釈の虚偽、ループ変数注釈漏れ）。

修正箇所の原則:
- **emitter / runtime の描画ロジックを変えて吸収してはならない**（spec-east.md §5, spec-agent.md §5）
- 修正対象は `src/toolchain/emit/<lang>/` 配下の source 型注釈、または `src/toolchain/emit/common/` 配下の source
- `src/toolchain/link/` 等、他 backend と共有される層に変更が波及する場合はプランナーに相談

### S3: 実行と parity 確認

コンパイルできた emitter バイナリに既存 fixture の manifest.json を食わせ、Python 版 emitter と同じ出力を吐くことを確認する。最低 1 fixture で stdout / 生成ソースが一致すれば S3 は達成とみなす。

## 進め方

- 各 backend の担当が自分の TODO に積まれた task を独立に進める
- 他 backend の進捗を待つ必要はない
- 共有層（`emit/common/`, `link/`, `common/`）の修正が出たときだけ情報共有し、重複作業を避ける
- S1 の段階で「emitter 本体の parse すら通らない」ような構文を発見したら、plan を更新して frontend parser の改修を別タスクとして切り出す

## 非対象

- pytra-cli.py 全体の selfhost（別タスク `P0-SELFHOST-*` で継続）
- parse / resolve / compile / link / optimize 層の source 整備（ただし emit から import している共通モジュールは対象）
- 新規 fixture 追加や emitter 機能拡張

## 決定ログ

- 2026-04-16: 起票。各 backend で並行着手できる単位に分解することで、全体 selfhost の blocker に引きずられずに emitter 層の selfhost-safe 化を進められると判断。
