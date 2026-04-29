# Top100 言語 coverage matrix

最終更新: 2026-04-30

## Source snapshot

- 出典: TIOBE Index for April 2026
- URL: https://www.tiobe.com/tiobe-index/
- 取得日: 2026-04-30
- 位置付け: 外部の人気指標スナップショット。Pytra では優先度付けに使い、技術的適性は別途 `backend` / `host` / `interop` / `syntax` / `defer` で判断する。

## 今回の実測

- 仮想環境: Docker Desktop CLI (`/Applications/Docker.app/Contents/Resources/bin/docker`) で `.devcontainer/Dockerfile` を直接 build。Dev Containers CLI は未検出のため未使用。
- toolchain: `.devcontainer/scripts/verify-toolchain.sh` は PASS。Python 3.12 / pytest / C/C++ / Java / .NET / PowerShell / Ruby / Lua / PHP / Go / Rust を確認。Swift は optional 未導入。`dart` / `zig` CLI も未導入。
- runtime east: `PYTHONPATH=src python3 tools/gen/regenerate_runtime_east.py` は `runtime-east total: 32 ok, 0 failed`。
- unit: `python3 -m pytest -q tools/unittest/toolchain2/test_tuple_unpack_emitter_hosts.py` は `4 passed`。
- emitter-host: `python3 src/pytra-cli.py -build src/toolchain/emit/cpp/cli.py --target dart -o work/tmp/verify_pytra_20260430/host_cpp_dart` は PASS、25 files。`--target zig` は PASS、30 files。
- fixture/sample/stdlib/selfhost/emitter-host matrix: `python3 tools/gen/gen_backend_progress.py` は JA/EN の `progress-preview` を生成。現行公開 matrix では fixture は C++ 161/161、sample/stdlib は全18 target で 18/18 / 16/16、selfhost は未完が多い。
- sample parity live check: `python3 tools/check/check_all_target_sample_parity.py --groups cpp --summary-dir work/tmp/verify_pytra_20260430/sample_parity_cpp` は runner の古い引数 drift 修正後に起動し、18 cases / pass 0 / fail 18。先頭 blocker は C++ runtime symbol `::int_` / `::print` / `::len` / `::min` / `::max` / `::enumerate` 未解決。

## 分類ルール

- `backend`: Pytra target として emit でき、progress matrix へ接続する。
- `host`: Pytra toolchain / emitter の host として扱う。
- `interop`: 既存 runtime / ABI / query engine との接続対象にする。
- `syntax`: backend 化判断に必要な構文・型・module 調査を先に行う。
- `defer`: text backend として扱う前に別設計が必要なため、解除条件を待つ。

## Matrix

| rank | language | category | current status | last blocker | next action |
|---:|---|---|---|---|---|
| 1 | Python | host | reference parser/resolver/toolchain source | selfhost matrix は full pass ではない | selfhost rows を段階的に埋める |
| 2 | C | interop | C ABI / C-family runtime adjacency | native C backend は未定義 | C++ runtime との境界を棚卸しする |
| 3 | C++ | backend | primary backend; fixture 161/161 | sample live check で runtime symbol drift | `::int_` / `::print` / `::len` lowering を修正する |
| 4 | Java | backend | target registered | host/parity は未完 | JVM host matrix を継続する |
| 5 | C# | backend | target registered | host/parity は未完 | Mono/.NET compile blocker を分類する |
| 6 | JavaScript | backend | target registered | selfhost 未完 | JS/TS row をまとめて再検証する |
| 7 | Visual Basic | syntax | backend candidate | profile / emitter 未作成 | VB.NET と Classic VB を分離評価する |
| 8 | SQL | interop | query/DSL lane | 通常 text backend ではない | external engine interop plan を作る |
| 9 | R | syntax | backend candidate | type/runtime 方針未定 | numeric/vector semantics を調査する |
| 10 | Delphi/Object Pascal | syntax | backend candidate | module/object model 未調査 | Pascal family profile を調査する |
| 11 | Scratch | defer | visual/block DSL | text backend ではない | intermediate DSL 変換条件を定義する |
| 12 | Perl | syntax | backend candidate | runtime semantics 未調査 | syntax smoke を作る |
| 13 | Fortran | syntax | backend candidate | array/numeric semantics 未調査 | numeric backend suitability を調査する |
| 14 | PHP | backend | target registered | host/parity は未完 | PHP host parity を進める |
| 15 | Go | backend | target registered; emitter-host PASS row あり | full selfhost 未完 | host parity JSON を増やす |
| 16 | Rust | backend | target registered | selfhost 未完 | Rust fixture fail を縮める |
| 17 | MATLAB | syntax | backend candidate | runtime/license 方針未定 | Octave interop 可否を調査する |
| 18 | Assembly language | defer | low-level target family | ISA 固有で一括 backend 不可 | WASM/LLVM lane と分離する |
| 19 | Swift | backend | target registered | Linux devcontainer では Swift 未導入 | optional Swift image/gate を検討する |
| 20 | Ada | syntax | backend candidate | runtime/toolchain 未調査 | GNAT availability を確認する |
| 21 | PL/SQL | syntax | backend candidate | DB runtime 前提 | SQL interop lane と接続する |
| 22 | Prolog | syntax | backend candidate | logic programming semantics 未調査 | unification/control model を調査する |
| 23 | COBOL | syntax | backend candidate | data division/runtime 未調査 | compiler availability を調査する |
| 24 | Kotlin | backend | target registered | host/parity は未完 | JVM common blockers を整理する |
| 25 | SAS | syntax | backend candidate | proprietary runtime 前提 | open substitute の有無を確認する |
| 26 | Classic Visual Basic | syntax | VB family candidate | Visual Basic と分類重複 | VB.NET との分離条件を記録する |
| 27 | Objective-C | syntax | backend candidate | ObjC runtime 方針未定 | C/Swift interop と比較する |
| 28 | Dart | backend | target registered; C++ emitter host 生成 PASS | devcontainer に `dart` CLI が無い | Dart CLI を隔離環境へ追加して compile/parity |
| 29 | Ruby | backend | target registered | host parity は未完 | generated host runtime require blocker を直す |
| 30 | Lua | backend | target registered | host parity は未完 | Lua runtime gate を再確認する |
| 31 | Lisp | syntax | backend candidate | dialect 未確定 | Common Lisp / Scheme を分離する |
| 32 | Julia | backend | target registered | host/selfhost 未完 | Julia compile/run gate を確認する |
| 33 | ML | syntax | backend candidate | dialect 未確定 | OCaml/SML と分離する |
| 34 | TypeScript | backend | target registered; emitter-host PASS row あり | full selfhost 未完 | TS host parity を拡張する |
| 35 | Haskell | syntax | backend candidate | lazy semantics 未調査 | strict subset 可否を調査する |
| 36 | VBScript | syntax | backend candidate | host/runtime obsolete | Windows/script host 前提を確認する |
| 37 | ABAP | syntax | backend candidate | proprietary runtime 前提 | interop/defer への降格条件を定義する |
| 38 | OCaml | syntax | backend candidate | ML family重複 | OCaml profile 調査を先行する |
| 39 | Zig | backend | target registered; C++ emitter host 生成 PASS | devcontainer に `zig` CLI が無い | Zig CLI を隔離環境へ追加して compile/parity |
| 40 | Caml | syntax | backend candidate | OCaml との重複 | OCaml row へ統合可否を判断する |
| 41 | Erlang | syntax | backend candidate | actor/runtime model 未調査 | BEAM lane を切る |
| 42 | X++ | syntax | backend candidate | proprietary runtime 前提 | defer 条件を確認する |
| 43 | Scala | backend | target registered | host/parity は未完 | Scala namespace blocker を直す |
| 44 | Transact-SQL | syntax | backend candidate | DB runtime 前提 | SQL interop lane と接続する |
| 45 | PowerShell | backend | target registered; devcontainer `pwsh` あり | host parity は未完 | PowerShell host parity を再実行する |
| 46 | GML | defer | game engine DSL | external engine 前提 | interop lane を検討する |
| 47 | LabVIEW | defer | visual/dataflow DSL | text backend ではない | model exchange 条件を調査する |
| 48 | Ladder Logic | defer | PLC DSL | safety/runtime 前提 | PLC interop 条件を調査する |
| 49 | Solidity | syntax | backend candidate | VM/security semantics 未調査 | EVM target suitability を調査する |
| 50 | (Visual) FoxPro | defer | legacy/proprietary lane | runtime 入手性が低い | preserve/defer 理由を明文化する |
| 51-100 | ActionScript | syntax | backend candidate | runtime obsolete | ECMAScript family との差分を調査する |
| 51-100 | Algol | defer | historical language | practical toolchain 目的が薄い | defer 理由を固定する |
| 51-100 | Apex | syntax | backend candidate | Salesforce runtime 前提 | proprietary interop 条件を確認する |
| 51-100 | Applescript | syntax | backend candidate | macOS automation 前提 | host/interop lane を調査する |
| 51-100 | Awk | syntax | backend candidate | text stream semantics 未調査 | POSIX toolchain smoke を作る |
| 51-100 | Bash | syntax | backend candidate | shell semantics 未調査 | Bourne shell と分離する |
| 51-100 | bc | defer | calculator DSL | narrow domain | interop helper 扱いを検討する |
| 51-100 | BCPL | defer | historical language | practical toolchain 目的が薄い | defer 理由を固定する |
| 51-100 | Bourne shell | interop | shell lane | Bash との重複 | POSIX shell subset を定義する |
| 51-100 | CFML | defer | server/runtime DSL | runtime 前提 | interop/defer 条件を記録する |
| 51-100 | CL (OS/400) | defer | platform-specific | IBM i 前提 | platform lane に分離する |
| 51-100 | Clojure | syntax | backend candidate | Lisp/BEAM/JVM family 差分 | JVM interop と比較する |
| 51-100 | CoffeeScript | syntax | backend candidate | JS transpiler 前提 | JS backend との重複を確認する |
| 51-100 | Curl | defer | niche/runtime 前提 | toolchain 入手性 | defer 理由を固定する |
| 51-100 | D | syntax | backend candidate | C-family backend 方針未定 | compiler smoke を調査する |
| 51-100 | Elixir | syntax | backend candidate | BEAM runtime 前提 | Erlang lane と接続する |
| 51-100 | F# | syntax | backend candidate | .NET functional lane | C# backend との共有可否を調査する |
| 51-100 | GAMS | defer | optimization DSL | solver/runtime 前提 | interop lane を検討する |
| 51-100 | Groovy | syntax | backend candidate | JVM dynamic lane | Java/Kotlin/Scala と比較する |
| 51-100 | Icon | defer | niche language | toolchain 入手性 | defer 理由を固定する |
| 51-100 | Inform | defer | interactive fiction DSL | domain-specific | DSL transform 条件を定義する |
| 51-100 | Io | defer | niche language | toolchain 入手性 | defer 理由を固定する |
| 51-100 | J | defer | array language | semantics 差分大 | APL family と比較する |
| 51-100 | J# | defer | obsolete .NET language | supported runtime 不明 | defer 理由を固定する |
| 51-100 | JScript | interop | JS family legacy | JavaScript と重複 | JS lane へ統合可否を判断する |
| 51-100 | JScript.NET | defer | obsolete .NET language | supported runtime 不明 | defer 理由を固定する |
| 51-100 | Logo | defer | education DSL | text backend 優先度低 | defer 理由を固定する |
| 51-100 | LotusScript | defer | platform-specific | Domino runtime 前提 | defer 理由を固定する |
| 51-100 | LPC | defer | MUD/domain runtime | niche runtime 前提 | defer 理由を固定する |
| 51-100 | Mojo | syntax | backend candidate | language/toolchain maturity | Python/C++ lane と比較する |
| 51-100 | MQL5 | interop | trading platform DSL | MetaTrader runtime 前提 | external platform interop 条件を定義する |
| 51-100 | NetLogo | defer | agent-based DSL | domain-specific | DSL transform 条件を定義する |
| 51-100 | Nim | backend | target registered | host/selfhost 未完 | Nim host parity を維持拡張する |
| 51-100 | OpenCL | syntax | backend candidate | accelerator/kernel lane | C/C++ interop と分離する |
| 51-100 | PL/I | defer | legacy language | practical toolchain 目的が薄い | defer 理由を固定する |
| 51-100 | Pure Data | defer | visual/dataflow DSL | text backend ではない | model exchange 条件を調査する |
| 51-100 | Q | defer | kdb+ runtime 前提 | proprietary/runtime-specific | interop/defer 条件を記録する |
| 51-100 | REBOL | defer | niche language | toolchain 入手性 | defer 理由を固定する |
| 51-100 | Ring | defer | niche language | toolchain 入手性 | defer 理由を固定する |
| 51-100 | RPG | defer | platform-specific | IBM i 前提 | platform lane に分離する |
| 51-100 | RPL | defer | calculator/platform DSL | narrow runtime | defer 理由を固定する |
| 51-100 | S | interop | R predecessor | R lane と重複 | R row へ統合可否を判断する |
| 51-100 | Small Basic | defer | education/runtime-specific | Visual Basic と重複 | VB family との関係を記録する |
| 51-100 | Smalltalk | syntax | backend candidate | object image/runtime semantics | VM interop 可否を調査する |
| 51-100 | Tcl | syntax | backend candidate | dynamic/string semantics | shell lane と比較する |
| 51-100 | V | syntax | backend candidate | C-family/toolchain maturity | compiler smoke を調査する |
| 51-100 | Vala/Genie | syntax | backend candidate | GObject/C transpile 前提 | C interop lane と比較する |
| 51-100 | VHDL | syntax | hardware DSL candidate | simulator/synthesis 前提 | HDL defer 条件を定義する |
| 51-100 | Wolfram | syntax | symbolic/runtime candidate | proprietary runtime 前提 | open kernel/interpreter 可否を調査する |
| 51-100 | Xojo | defer | proprietary IDE/runtime | text backend 優先度低 | defer 理由を固定する |

## 次アクション

1. `docs/ja/progress/top100-language-coverage.md` を `gen_backend_progress.py` または専用 generator の出力対象に移す。
2. Dart / Zig CLI を devcontainer に追加するか、別 image として分離し、今回 PASS した host 生成物を compile/parity まで進める。
3. sample parity の C++ runtime symbol drift (`::int_` / `::print` / `::len`) を修正し、live sample check と既存 sample matrix の差分をなくす。
