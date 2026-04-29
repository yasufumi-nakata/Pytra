# P2 Top100 language coverage plan

## 目的

使用上位 100 言語への適応を、全言語を一律 backend 化する計画ではなく、`backend` / `host` / `interop` / `syntax` / `defer` の分類で継続管理する。

## 2026-04-29 source snapshot

- 外部 Top100 source はまだ固定していない。本 run では、リポジトリ内の現行 coverage を基準 snapshot とし、外部ランキングの採用は次アクションに残す。
- 現行 backend progress snapshot: `docs/ja/progress/backend-progress-summary.md` の 18 言語（`cpp`, `rs`, `cs`, `ps1`, `js`, `ts`, `dart`, `go`, `java`, `scala`, `kotlin`, `swift`, `ruby`, `lua`, `php`, `nim`, `julia`, `zig`）。
- 現行 build target snapshot: `src/pytra-cli.py -build` は `cpp`, `go`, `rs`, `cs`, `java`, `scala`, `kotlin`, `ts`, `js`, `nim`, `swift`, `julia`, `powershell`, `ps1`, `zig`, `dart`, `lua`, `php`, `ruby` を受け付ける。

## 分類

| 分類 | 意味 | 現在の扱い |
|---|---|---|
| `backend` | Pytra の emit / runtime / parity 対象として実装する | 現行 18 言語を対象に継続 |
| `host` | 既存 backend で Pytra の emitter / runtime を host する | emitter-host/selfhost マトリクスで継続 |
| `interop` | FFI、VM、外部 CLI、既存 runtime 連携で扱う | Top100 source 固定後に選別 |
| `syntax` | frontend/parser の構文受理や変換元として扱う | Python source 以外の入力計画で扱う |
| `defer` | 現時点では対応しない | source snapshot 固定時に理由を明記 |

## 実測コマンド

2026-04-29 は `.devcontainer/` と Dockerfile が存在しないため、Docker Engine 確認後、`/Applications/Docker.app/Contents/Resources/bin/docker` と `python:3.12-slim` を使った隔離実行で確認した。

```bash
/Applications/Docker.app/Contents/Resources/bin/docker version
PATH=/Applications/Docker.app/Contents/Resources/bin:$PATH \
  docker run --rm --pull=never hello-world
PATH=/Applications/Docker.app/Contents/Resources/bin:$PATH \
  docker run --rm -v "$PWD":/workspace -w /workspace -e PYTHONPATH=src python:3.12-slim \
  python -m unittest tools.unittest.tooling.test_pytra_cli2 -v
PATH=/Applications/Docker.app/Contents/Resources/bin:$PATH \
  docker run --rm -v "$PWD":/workspace -w /workspace -e PYTHONPATH=src python:3.12-slim \
  sh -lc 'for target in dart lua php zig powershell; do python src/pytra-cli.py -build test/fixture/source/py/core/add.py --target "$target" -o "work/tmp/verify_pytra_20260429/build_add_$target"; done'
```

## 最後の blocker

- 外部 Top100 source が未固定のため、100 言語の分類表はまだ作れない。
- Docker 内 `python:3.12-slim` には `pwsh` / `powershell` がなく、PowerShell の run parity は未実行。
- Ruby は focused fixture 5/5 PASS だが、`os_glob_extended` と sample `01_mandelbrot` は stdout mismatch が残る。

## 次アクション

1. 外部 Top100 source を 1 つに固定し、取得日・URL・保存場所をこのファイルへ追記する。
2. 100 言語を `backend` / `host` / `interop` / `syntax` / `defer` に分類する。
3. `backend` / `host` 候補は既存 progress matrix に接続し、`interop` / `syntax` / `defer` は個別 plan へ切り出す。
