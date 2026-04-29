# P1-EMITTER-HOST-MATRIX: emitter host マトリクスの新設と全言語 PASS

最終更新: 2026-04-29

## 背景

selfhost マトリクス（`backend-progress-selfhost.md`）は「pytra-cli.py 全体を変換した full selfhost binary で emit + parity」を見ている。これは `run_selfhost_parity.py` の結果（`.parity-results/selfhost_*.json`）から生成される。

一方、P1-HOST-CPP-EMITTER は「C++ emitter（16 モジュール）だけを各言語に変換して host し、Python 版と同じ C++ 出力を生成できるか」を検証する。full selfhost とは対象が異なるため、selfhost マトリクスには直接反映できない。

## 目的

- **emitter host マトリクス** を progress に新設する
- 行: 18 backend 言語（C++ emitter の host 言語）
- 列: C++ emitter の host 結果（build PASS / parity PASS）
- **全言語で C++ emitter host PASS** を中間目標にする
- full selfhost（pytra-cli.py 全体）は次のフェーズ

## マトリクス定義

| host 言語 | build | parity |
|---|---|---|
| cpp | 🟩 | 🟩 |
| go | ? | ? |
| nim | ? | ? |
| rs | ⬜ | ⬜ |
| ... | ... | ... |

- **build**: `python3 src/pytra-cli.py -build src/toolchain/emit/cpp/cli.py --target <lang>` + target 言語の compiler で build が通る
- **parity**: build した emitter binary に fixture の linked manifest を食わせて、Python 版 emitter と同じ C++ 出力を生成する

## 結果の記録方式

各 backend 担当が parity 確認後、`.parity-results/emitter_host_<lang>.json` に結果を書き込む。

```json
{
  "host_lang": "go",
  "hosted_emitter": "cpp",
  "build_status": "ok",
  "parity_status": "ok",
  "parity_fixture_pass": 161,
  "parity_fixture_fail": 0,
  "timestamp": "2026-04-29 12:00:00"
}
```

`gen_backend_progress.py` がこの JSON を読んで emitter host マトリクスを生成する。

## サブタスク

1. [ ] [ID: P1-EHOST-MATRIX-S1] `gen_backend_progress.py` に emitter host マトリクス生成を追加する
2. [ ] [ID: P1-EHOST-MATRIX-S2] `progress-preview/` に `backend-progress-emitter-host.md` を出力するようにする
3. [ ] [ID: P1-EHOST-MATRIX-S3] 各 backend の P1-HOST-CPP-EMITTER タスクの S2 を、`.parity-results/emitter_host_<lang>.json` の書き込みに更新する
4. [ ] [ID: P1-EHOST-MATRIX-S4] 全 18 言語で emitter host parity PASS を達成する（中間目標）

## 決定ログ

- 2026-04-29: 起票。selfhost マトリクス（full compiler）と emitter host マトリクス（emitter のみ）を分離する方針を決定。emitter host 全言語 PASS を full selfhost 前の中間目標とする。
