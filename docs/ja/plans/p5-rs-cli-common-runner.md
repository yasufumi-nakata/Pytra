# P5-RS-CLI-COMMON: Rust cli.py を共通ランナーに移行する

最終更新: 2026-04-03

## 背景

全17言語の cli.py のうち、Rust だけが共通ランナー（`toolchain2.emit.common.cli_runner`）を使わず 235 行の独自実装を持っている。独自部分は以下の2つ:

1. **type_id テーブル生成**: `_generate_type_id_table_rs` で `PYTRA_TID_*` 定数の Rust 版を生成。manifest の `type_id_resolved_v1` から定数テーブルを作る
2. **package mode**: `--package` オプションで `Cargo.toml` + `src/lib.rs` + `src/main.rs` を生成。selfhost 用

## 前提条件

- **P0-ISINSTANCE-DETID 全完了**: EAST3 から `PYTRA_TID_*` が完全に消え、Rust emitter も `expected_type_name` ベースに移行済み。これにより type_id テーブル生成が不要になる
- **Rust emitter が `x is Type` 相当のネイティブ判定**（`if let` / `match`）に移行済み

## 方針

1. type_id テーブル生成を削除（前提条件で不要になる）
2. runtime コピー（`_copy_rs_runtime_files`）を `post_emit` に移動
3. package mode（`Cargo.toml` + `lib.rs` + `main.rs` 生成）を `post_emit` に移動
4. manifest 読み・モジュールループ・引数解析を共通ランナーに委譲
5. `--package` オプションは共通ランナーの `_parse_args` に追加するか、Rust の `post_emit` 内で `sys.argv` から読む

## 完了後の cli.py イメージ

```python
from toolchain2.emit.common.cli_runner import run_emit_cli
from toolchain2.emit.rs.emitter import emit_rs_module

def _post_emit_rs(output_dir: Path) -> None:
    _copy_rs_runtime(output_dir)
    if _is_package_mode():
        _write_cargo_toml(output_dir)
        _write_lib_rs(output_dir)
        _write_main_rs(output_dir)

def main() -> int:
    import sys
    return run_emit_cli(emit_rs_module, sys.argv[1:], default_ext=".rs", post_emit=_post_emit_rs)
```

## サブタスク

1. [ ] [ID: P5-RS-CLI-S1] Rust emitter を `expected_type_name` ベースに移行する（P0-ISINSTANCE-DETID の Rust 版）
2. [ ] [ID: P5-RS-CLI-S2] `_generate_type_id_table_rs` と `_manifest_type_id_table` を削除する
3. [ ] [ID: P5-RS-CLI-S3] runtime コピーと package mode を `post_emit` に移動し、共通ランナーに委譲する
4. [ ] [ID: P5-RS-CLI-S4] Rust parity に回帰がないことを確認する

## 決定ログ

- 2026-04-03: 全17言語の cli.py を共通ランナーに移行。Rust のみ独自実装が残った。type_id テーブル廃止後に移行可能として計画起票。
