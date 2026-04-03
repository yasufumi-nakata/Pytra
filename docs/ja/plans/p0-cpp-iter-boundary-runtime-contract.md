# P0 C++ iter boundary runtime contract

最終更新: 2026-04-03

## 目的

`P0-CPP-VARIANT-S10` を進める前提として、C++ backend で `ObjIterInit` / `ObjIterNext` をどう扱うかの契約を固定する。

現状は次のねじれがある。

- `src/toolchain2/compile/lower.py` は `iter.init` / `iter.next` を `ObjIterInit` / `ObjIterNext` として生成する
- `src/toolchain2/emit/cpp/emitter.py` は direct `ObjIterInit` / `ObjIterNext` を処理しない
- `src/runtime/cpp/` には `py_iter_or_raise` / `py_next_or_stop` free helper が存在しない
- さらに linked runtime の generic helper、現状では [predicates.east](../../runtime/east/built_in/predicates.east) の `py_any` / `py_all` が `ForCore(iter_plan.init_op=ObjIterInit, next_op=ObjIterNext)` を前提にしている

この状態では、`lower.py` から iter boundary を消す作業と、C++ runtime / emitter の契約整理が密結合になる。

## 進め方

1. `P0-CPP-VARIANT-S10B`
   - C++ runtime / emitter で採用する iter boundary 契約を決める
   - 候補:
     - `ObjIterInit` / `ObjIterNext` を direct emit する
     - free helper を再導入する
     - method call 契約を runtime core に戻す
   - 追加前提:
     - linked runtime の generic iter helper をどう置き換えるかも同時に決める
     - 現状は `src/runtime/east/built_in/predicates.east` の `py_any` / `py_all` が C++ backend に iter boundary seam を再流入させる

2. `P0-CPP-VARIANT-S10`
   - 上記契約に沿って `lower.py` から `resolved_type="object"` Boxing と iter boundary を段階的に削る

## 2026-04-03 時点の整理

- canonical source から `iter_ops.py` は消えており、旧 blocker は現状の repo には存在しない
- C++ 向け lower の fixture 全走査では、non-explicit dynamic path の `resolved_type="object"` は 0
- residual seam は
  - explicit object 契約: `trait_basic`, `trait_with_inheritance`, `typed_container_access`
  - bare `Callable -> object` 境界
  - runtime generic iter helper: `src/runtime/east/built_in/predicates.east` の `py_any` / `py_all`

## 完了条件

- iter boundary の residual seam が explicit object / bare `Callable` とは別契約として切り分けられている
- runtime generic iter helper の依存先が `predicates.east` であることを記録し、`S10` 本体から独立に追跡できる
