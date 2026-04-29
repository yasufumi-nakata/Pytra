# P1-EMITTER-HOST-MATRIX: emitter host マトリクス（全言語 × 全言語）

最終更新: 2026-04-29

## 背景

selfhost マトリクス（`backend-progress-selfhost.md`）は「pytra-cli.py 全体を変換した full selfhost binary で emit + parity」を見ている。これは対象が大きく（31 モジュール）、全言語で PASS するには時間がかかる。

一方、各 backend の emitter は subprocess で独立起動する自己完結プログラム（16 モジュール前後）であり、これを他の言語で host するのはより現実的な中間目標である。

## 目的

- **emitter host マトリクス** を progress に新設する
- **行**: host 言語（emitter を変換・実行する言語）
- **列**: hosted emitter（どの言語向け emitter を host しているか）
- **セル**: host 言語で hosted emitter を変換 + build + parity PASS
- **中間目標**: 全セルで PASS（各言語が全言語の emitter を host できる状態）
- full selfhost（pytra-cli.py 全体）は次のフェーズ

## マトリクス構造

```
            hosted emitter (emit 先)
            cpp   rs   go   ts   cs   ...
host   cpp   🟩   ⬜   ⬜   ⬜   ⬜
lang   rs    ⬜   ⬜   ⬜   ⬜   ⬜
       go    🟩   ⬜   ⬜   ⬜   ⬜
       ts    🟩   ⬜   ⬜   ⬜   ⬜
       nim   🟩   ⬜   ⬜   ⬜   ⬜
       ...
```

- 対角セル（cpp→cpp, go→go 等）は「自分の emitter を自分で host」= emitter selfhost
- 非対角セル（go→cpp 等）は「他言語の emitter を host」= cross-host

## 結果の記録方式

各セルの結果は `.parity-results/emitter_host_<host_lang>.json` に記録する。1 ファイルに複数の hosted emitter の結果を持てる構造にする。

```json
{
  "host_lang": "go",
  "emitters": {
    "cpp": {
      "build_status": "ok",
      "parity_status": "ok",
      "parity_fixture_pass": 161,
      "parity_fixture_fail": 0,
      "timestamp": "2026-04-29 12:00:00"
    },
    "rs": {
      "build_status": "fail",
      "parity_status": "not_tested",
      "timestamp": "2026-04-29 13:00:00"
    }
  }
}
```

`gen_backend_progress.py` がこの JSON を読んで N×N マトリクスを生成する。

## 検証コマンド

```bash
# Go で C++ emitter を host
python3 src/pytra-cli.py -build src/toolchain/emit/cpp/cli.py --target go -o work/selfhost/host-cpp/go/

# Go で Rust emitter を host
python3 src/pytra-cli.py -build src/toolchain/emit/rs/cli.py --target go -o work/selfhost/host-rs/go/
```

## サブタスク

1. [x] [ID: P1-EHOST-MATRIX-S1] `gen_backend_progress.py` に emitter host マトリクス生成を追加する
2. [x] [ID: P1-EHOST-MATRIX-S2] `progress-preview/backend-progress-emitter-host.md` を出力するようにする
3. [x] [ID: P1-EHOST-MATRIX-S3] 各 backend の P1-HOST-CPP-EMITTER タスクの S2 で `.parity-results/emitter_host_<lang>.json` に結果を書き込むよう更新する
4. [x] [ID: P1-EHOST-MATRIX-S4] JSON 形式を N×N 対応に拡張する（1ファイルに複数 hosted emitter の結果を持てるようにする）
5. [x] [ID: P1-EHOST-MATRIX-S5] `gen_backend_progress.py` を N×N マトリクス表示に対応させる

全 18 言語での emitter host PASS は中間目標として設定するが、実作業は各 backend 担当が P1-HOST-CPP-EMITTER-<LANG> 等で進める。

## 決定ログ

- 2026-04-29: 起票。selfhost マトリクス（full compiler）と emitter host マトリクス（emitter のみ）を分離する方針を決定。emitter host 全言語 PASS を full selfhost 前の中間目標とする。
- 2026-04-29: [ID: P1-EHOST-MATRIX-S1/S2/S3] C++ emitter host の列だけで初版マトリクスを生成。Go, TS, Nim が PASS。
- 2026-04-29: マトリクスを全言語 × 全言語の N×N 構造に拡張する方針を決定。C++ emitter の列は初版の実績を維持しつつ、他 emitter の列を追加可能にする。
- 2026-04-29: [ID: P1-EHOST-MATRIX-S4/S5] `emitter_host_<host_lang>.json` の `emitters` map を正本形式として固定し、`gen_backend_progress.py` を host 言語 × hosted emitter の N×N 表示へ対応させた。既存の単一 `hosted_emitter` 形式と `hosted_emitters` / `results` alias は後方互換として受理する。
