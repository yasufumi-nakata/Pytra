# P1-SWIFT-EMITTER-S1/S2 Swift toolchain2 bootstrap

最終更新: 2026-04-02

## 目的

- `src/toolchain2/emit/swift/` に Swift emitter の起点を作る
- `src/runtime/swift/mapping.json` と parity harness の Swift 導線を追加する
- Swift backend を「未接続」状態から fixture を段階的に回せる状態にする

## このターンで入れたもの

- `src/toolchain2/emit/swift/` を追加し、toolchain2 から呼べる `emit_swift_module()` を定義
- `src/toolchain2/emit/profiles/swift.json` を追加
- `src/runtime/swift/mapping.json` を追加
- `tools/check/runtime_parity_check_fast.py` に Swift の emit/copy/build/run を追加
- `src/runtime/swift/image_runtime.swift` を追加
- `src/runtime/swift/built_in/py_runtime.swift` に bootstrap に必要な helper を追加

## ここまでで確認できたこと

- Swift target が parity harness から起動できる
- `add`, `assign`, `alias_arg`, `class`, `class_instance`, `if_else`, `for_range`, `import_math_module` は PASS
- `collections` と `from_import_symbols` は emit/run まで進み、残りは container helper と output parity の詰め

## 残課題

- container mutation (`dict.pop`, `dict.setdefault`, set/list mutation) の戻り値と破壊的更新を整える
- `from_import_symbols` の output mismatch を潰す
- fixture 全量 parity を通す
- emitter hardcode lint の大量違反を別タスクで解消する
