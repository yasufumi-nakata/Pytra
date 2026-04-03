# P5-PARITY-EMIT-UNIFY: runtime_parity_check_fast.py の emit ロジックを共通化する

最終更新: 2026-04-03

## 背景

`tools/check/runtime_parity_check_fast.py` の `_transpile_in_memory` 関数に 18 言語分の if/elif チェーンがある。各言語の `emit_<lang>_module` を直接 import し、module_kind 分岐、runtime コピー、emit context 注入を言語ごとに手書きしている。新しい言語を追加するたびに parity check を修正する必要がある。

一方、各言語の `cli.py` は共通ランナー（`toolchain2.emit.common.cli_runner`）に移行済み。emit 関数 + post_emit で統一されている。

## 方針

parity check は `tools/` 配下で selfhost 対象外なので `importlib` による動的 import が使える。emit ロジックを以下のように簡略化する:

```python
import importlib

def _emit_modules(linked_modules, target, output_dir):
    # 動的 import で emit 関数を取得
    lang = "ts" if target == "js" else target
    mod = importlib.import_module(f"toolchain2.emit.{lang}.emitter")
    emit_fn = getattr(mod, f"emit_{lang}_module")

    for m in linked_modules:
        code = emit_fn(m.east_doc)
        if code.strip() == "":
            continue
        out_name = m.module_id.replace(".", "_") + _ext_for_target(target)
        output_dir.joinpath(out_name).write_text(code, encoding="utf-8")

    # post_emit (runtime copy) も動的に取得
    try:
        cli_mod = importlib.import_module(f"toolchain2.emit.{lang}.cli")
        post_emit = getattr(cli_mod, "_copy_{lang}_runtime", None)
        if post_emit:
            post_emit(output_dir)
    except (ImportError, AttributeError):
        pass
```

### C++ の特殊処理

C++ は `emit_fn(east_doc) → str` ではなく `direct_emit_fn(east_doc, output_dir) → int`。parity check で C++ を判定して `_emit_cpp_direct`（cli.py で定義済み）を呼ぶ。C++ だけ 1 行の if 分岐が残るが、18 言語分の if/elif が消える。

### 削除されるもの

- `_transpile_in_memory` 内の 18 言語 if/elif チェーン
- 各言語の `from toolchain2.emit.<lang>.emitter import emit_<lang>_module`（ファイル先頭の静的 import）
- `_copy_<lang>_runtime` 関数群（parity check 内に重複実装されているもの）
- `_inject_basic_module_id` ヘルパー（共通ランナーの `_cli_*` メタデータで代替）

### emit 関数名の不統一への対処

一部の言語で emit 関数名が不統一（ruby: `transpile_to_ruby`, powershell: `emit_ps`）。動的 import で `emit_{lang}_module` を探して見つからなければフォールバック名を試す。または、各言語の emitter.py に `emit_{lang}_module` エイリアスを追加して統一する（こちらが望ましい）。

## 対象

- `tools/check/runtime_parity_check_fast.py` — emit ループの共通化
- 各言語の `emitter.py` — emit 関数名の統一（必要な場合）

## 非対象

- `toolchain2/emit/common/cli_runner.py` の変更（既に完成済み）
- `pytra-cli2.py` の変更（subprocess 経由で変更不要）
- emitter 本体のロジック変更

## 受け入れ基準

- [ ] `_transpile_in_memory` の if/elif チェーンが動的 import ベースに置換されている
- [ ] 新しい言語を追加するときに parity check を修正する必要がない
- [ ] C++ parity に回帰がない（C++ だけ direct_emit_fn を使う分岐は許容）
- [ ] 既存の全言語の parity check が動作する

## サブタスク

1. [ ] [ID: P5-PARITY-EMIT-S1] 各言語の emitter.py で emit 関数名を `emit_<lang>_module` に統一する（ruby: `transpile_to_ruby` → エイリアス追加、powershell: `emit_ps` → エイリアス追加）
2. [ ] [ID: P5-PARITY-EMIT-S2] `_transpile_in_memory` の emit ループを動的 import + 共通ループに置換する
3. [ ] [ID: P5-PARITY-EMIT-S3] parity check 内の `_copy_<lang>_runtime` 重複実装を削除し、cli.py の post_emit に委譲する
4. [ ] [ID: P5-PARITY-EMIT-S4] 全言語の parity check（fixture 代表ケース）に回帰がないことを確認する

## 決定ログ

- 2026-04-03: 各言語の cli.py を共通ランナーに移行完了。同じパターンで parity check の emit ロジックも共通化する計画を起票。
