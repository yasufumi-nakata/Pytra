<a href="../../en/todo/ts.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — TypeScript / JavaScript backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-29

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**

## 現状

- toolchain2 に TS/JS emitter は未実装（`src/toolchain2/emit/ts/`, `src/toolchain2/emit/js/` が存在しない）
- runtime は `src/runtime/ts/`, `src/runtime/js/` に存在する（旧 toolchain1 時代の実装）
- 旧 toolchain1 の TS/JS emitter は `src/toolchain/emit/ts/`, `src/toolchain/emit/js/` に存在するが、toolchain2 への移行が必要

## 設計方針

TypeScript emitter を先に実装し、JavaScript は型注釈の出力を抑制するフラグで対応する。

- EAST3 には完全な型情報がある。TS emitter はこれを素直に型注釈付きで出力する
- JS モードは同じ emitter で型注釈を省略するだけ（`--strip-types` または `--target js`）
- emitter を2本作る必要はない。TS emitter 1本 + フラグで JS/TS の両方をカバーする

## 未完了タスク

### P8-TS-EMITTER: TypeScript emitter を toolchain2 に新規実装する

前提: Go emitter（参照実装）と CommonRenderer が安定してから着手。

1. [ ] [ID: P8-TS-EMITTER-S1] `src/toolchain2/emit/ts/` に TypeScript emitter を新規実装する — CommonRenderer + override 構成。TS/JS 固有のノード（prototype chain、arrow function、destructuring 等）だけ override として残す
2. [ ] [ID: P8-TS-EMITTER-S2] `src/runtime/ts/mapping.json` を作成し、runtime_call の写像を定義する
3. [ ] [ID: P8-TS-EMITTER-S3] fixture 132 件 + sample 18 件の TS emit 成功を確認する
4. [ ] [ID: P8-TS-EMITTER-S4] TS runtime を toolchain2 の emit 出力と整合させる
5. [ ] [ID: P8-TS-EMITTER-S5] fixture + sample の TS compile + run parity を通す（tsc + node 実行）
6. [ ] [ID: P8-TS-EMITTER-S6] 型注釈抑制フラグ（`--strip-types` or `--target js`）を追加し、JS 出力をカバーする
7. [ ] [ID: P8-TS-EMITTER-S7] fixture + sample の JS run parity を通す（node 実行）

### P12-TS-SELFHOST: TS emitter で toolchain2 を TypeScript に変換し tsc build を通す

前提: P8-TS-EMITTER 完了後に着手。

1. [ ] [ID: P12-TS-SELFHOST-S0] selfhost 対象コード（`src/toolchain2/` 全 .py）で戻り値型の注釈が欠けている関数に型注釈を追加する — resolve が `inference_failure` にならない状態にする（P4/P6/P9 と共通。先に完了した側の成果を共有）
2. [ ] [ID: P12-TS-SELFHOST-S1] toolchain2 全 .py を TS に emit し、tsc build が通ることを確認する
3. [ ] [ID: P12-TS-SELFHOST-S2] tsc build 失敗ケースを emitter/runtime の修正で解消する（EAST の workaround 禁止）
4. [ ] [ID: P12-TS-SELFHOST-S3] selfhost 用 TS golden を配置し、回帰テストとして維持する
