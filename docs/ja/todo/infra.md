<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-30

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260330.md) / [P10-REORG アーカイブ](archive/20260330-p10reorg.md) を参照。

## 未完了タスク

### P2-SAMPLE-BENCHMARK: sample parity check で実行時間を自動計測し README に反映する

文脈: [docs/ja/plans/p2-sample-benchmark.md](../plans/p2-sample-benchmark.md)

1. [ ] [ID: P2-BENCH-S1] parity check（fast 版）の sample 実行時に、Python と各ターゲットの実行時間（秒）を計測し `.parity-results/<target>_sample.json` の各ケースに `elapsed_sec` フィールドとして記録する
2. [ ] [ID: P2-BENCH-S2] Python 実行の計測結果を `.parity-results/python_sample.json` に記録する（比較基準）
3. [ ] [ID: P2-BENCH-S3] `tools/gen/gen_sample_benchmark.py` を作成する — `.parity-results/*_sample.json` を読み、`sample/README-ja.md` と `sample/README.md` の「実行速度の比較」テーブルを自動更新する（日英同時生成）
4. [ ] [ID: P2-BENCH-S4] 計測プロトコルを既存の計測条件（warmup=1, repeat=5, 中央値）に合わせるか、新しいプロトコルを定義する
5. [ ] [ID: P2-BENCH-S5] parity check の末尾で、前回生成から10分以上経過していれば `gen_sample_benchmark.py` を自動実行する（進捗マトリクスと同じ仕組み）

### P6-EMITTER-LINT: emitter 責務違反チェッカーの新設

文脈: [docs/ja/plans/p6-emitter-lint.md](../plans/p6-emitter-lint.md)

1. [x] [ID: P6-EMITTER-LINT-S1] `tools/check/check_emitter_hardcode_lint.py` を作成する（6カテゴリ grep チェック実装済み、現在 50 件の違反を検出）
2. ~~[ID: P6-EMITTER-LINT-S2] allowlist 機構を用意する~~ — **削除**: toolchain2 の C++ emitter は書き直しのため歴史的負債がなく、allowlist 不要。
3. [x] [ID: P6-EMITTER-LINT-S3] 結果を言語 × カテゴリのマトリクスとして stdout 出力（--verbose / --lang / --category オプション付き）
4. [x] [ID: P6-EMITTER-LINT-S4] 単独手動実行スクリプトとして完結（exit code 常に 0、他スクリプトへの組み込みなし）
5. [ ] [ID: P6-EMITTER-LINT-S5] 誤検知を減らすための除外ルールを追加する:
   - `mapping.json` ファイル自体を検査対象から除外する
   - `code_emitter.py`（mapping 読み込み共通基盤）を検査対象から除外する
   - `types.py`（型写像テーブル。`"Exception": "Error"` 等は正当）を検査対象から除外する
   - コメント行（`#` で始まる行）を除外する
   - `🟩0` を `🟩` に短縮する（0 件なら数字は冗長）

### P11-VERSION-GATE: toolchain2 用バージョンチェッカーの新設

前提: toolchain2 への完全移行後に着手。

1. [ ] [ID: P11-VERGATE-S1] `src/toolchain2/` 向けの `transpiler_versions.json` を新設する（toolchain1 の `src/toolchain/misc/transpiler_versions.json` は廃止）
2. [ ] [ID: P11-VERGATE-S2] toolchain2 のディレクトリ構成に合わせた shared / 言語別の依存パスを定義する
3. [ ] [ID: P11-VERGATE-S3] バージョンチェッカーを新しく書く（PATCH 以上の bump で OK とする。MINOR/MAJOR はユーザーの明示指示がある場合のみ）
4. [ ] [ID: P11-VERGATE-S4] 旧チェッカー（`tools/check/check_transpiler_version_gate.py`）と旧バージョンファイルを廃止する

### P20-INT32: int のデフォルトサイズを int64 → int32 に変更

文脈: [docs/ja/plans/p4-int32-default.md](../plans/p4-int32-default.md)

前提: Go selfhost 完了後に着手。影響範囲が大きいため P4 → P20 に降格。

1. [ ] [ID: P20-INT32-S1] spec-east.md / spec-east2.md の `int` → `int32` 正規化ルール変更
2. [ ] [ID: P20-INT32-S2] resolve の型正規化を修正
3. [ ] [ID: P20-INT32-S3] sample 18 件のオーバーフロー確認 + 必要な箇所を `int64` に明示
4. [ ] [ID: P20-INT32-S4] golden 再生成 + 全 emitter parity 確認
