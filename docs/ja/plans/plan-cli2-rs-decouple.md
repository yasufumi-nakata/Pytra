# 計画: pytra-cli2.py から Rust emit 固有 import を分離 (P0-CLI2-RS-DECOUPLE)

## 背景

`pytra-cli2.py` は C++ emit 経路を subprocess 委譲に切り替えたが、Rust emit 経路はまだ top-level で `toolchain2.emit.rs.emitter` と `toolchain2.link.manifest_loader` に依存している。

このため C++ selfhost で `src/pytra-cli2.py` を transpile すると、不要な Rust emitter とその依存が include graph に入り、`shutil.h` のような C++ compile 不能な header まで引き込まれる。

## 現状

- `src/pytra-cli2.py` に `from toolchain2.emit.rs.emitter import emit_rs_module`
- `src/pytra-cli2.py` に `from toolchain2.link.manifest_loader import load_linked_output`
- `_emit_rs()` / `_write_rs_package_files()` / `_copy_rs_runtime_files()` / `_manifest_type_id_table()` / `_generate_type_id_table_rs()` が `pytra-cli2.py` に残っている

## 方針

- Rust emit も C++ と同じく `toolchain2.emit.rs.cli` へ移す
- `pytra-cli2.py` は `python3 -m toolchain2.emit.rs.cli ...` を subprocess で呼ぶだけにする
- `-emit --target rs` と `-build --target rs` の挙動は維持する

## 具体的な変更

1. `src/toolchain2/emit/rs/cli.py` を追加し、manifest 読み込み、package emit、runtime file copy、type-id table 生成を移す
2. `src/pytra-cli2.py` から Rust emitter / manifest loader の top-level import を削除する
3. `src/pytra-cli2.py` の Rust emit/build 経路を subprocess 委譲へ変更する
4. `tools/unittest/tooling/test_pytra_cli2.py` に Rust emit import の非流入回帰を追加する

## 完了条件

- `pytra-cli2.py` の top-level import から Rust emit / manifest loader が消えている
- `pytra-cli2.py -emit --target rs ...` と `-build --target rs ...` が通る
- C++ selfhost 用に生成した `pytra_cli2.h` に `toolchain2/emit/rs/emitter.h` が含まれない

## 完了メモ

- `src/toolchain2/emit/rs/cli.py` を追加し、Rust emit の manifest 読み込み、package 出力、runtime copy を `pytra-cli2.py` から分離した
- `src/pytra-cli2.py` は Rust emit を `python3 -m toolchain2.emit.rs.cli` へ subprocess 委譲し、top-level の Rust emitter / manifest loader import を削除した
- `PYTHONPATH=src python3 src/pytra-cli2.py -build sample/py/17_monte_carlo_pi.py --target rs --rs-package -o work/tmp/cli2_rs_emit` は成功した
- `PYTHONPATH=src python3 src/pytra-cli2.py -build src/pytra-cli2.py --target cpp -o work/selfhost/build/cpp/emit` で生成した `work/selfhost/build/cpp/emit/pytra_cli2.h` には `toolchain2/emit/rs/emitter.h` も `shutil.h` も含まれない
