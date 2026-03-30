<a href="../../en/plans/p10-cpp-typetable-redesign.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P10-CPP-TYPETABLE-REDESIGN

## 背景

`src/runtime/cpp/core/object.h` の `g_type_table` は `Object<T>` の破棄時に deleter を引くためだけに残っていた。一方で user class の `isinstance` / `issubclass` 判定は generated `built_in/type_id.*` の `id_table` と `py_runtime_object_type_id(...)` で完結しており、toolchain2 C++ emitter が各 module で `py_tid_register_known_class_type(...)` を呼ぶ設計は二重管理になっていた。

## 棚卸し

- `g_type_table` の実利用は `Object<T>::release()` / `Object<void>::release()` の destructor dispatch と unit test の初期化だけだった。
- `py_tid_register_known_class_type(...)` の実利用は toolchain2 C++ emitter が出す local helper だけだった。
- `PYTRA_TID_*` は built-in scalar/container/object の runtime 定数として広く使われているため、P10 では撤去対象に含めない。

## 設計

- `ControlBlock` に `void (*deleter)(void*)` を持たせ、`make_object<T>` と POD boxing constructor で具体型の deleter を焼き込む。
- `Object<T>` / `Object<void>` の `release()` は `cb->deleter` を直接呼ぶ。これで global type table は不要になる。
- user class の subtype 判定は generated `id_table` を正本とし、toolchain2 emitter から local `py_tid_register_known_class_type(...)` helper を除去する。
- `pytra.built_in.type_id` と `core/type_id_support.h` から dead な known-registration API を削除する。

## 検証

- targeted unit:
  - `tools/unittest/emit/cpp/test_object_t.py`
  - `tools/unittest/emit/cpp/test_cpp_runtime_type_id.py`
  - `tools/unittest/emit/cpp/test_cpp_runtime_iterable.py`
- parity:
  - `PYTHONPATH=src:tools python3 tools/check/runtime_parity_check_fast.py --targets cpp --case-root fixture --east3-opt-level 2`
  - `PYTHONPATH=src:tools python3 tools/check/runtime_parity_check_fast.py --targets cpp --case-root sample --east3-opt-level 2`

## 実施結果

- `tools/unittest/emit/cpp/test_object_t.py`: PASS
- `PYTRA_GENERATED_CPP_DIR=/workspace/Pytra/work/tmp/p10_typetable/class_instance_emit python3 tools/unittest/emit/cpp/test_cpp_runtime_type_id.py`: PASS
- `class_instance.py` / `isinstance_user_class.py` の C++ build で local `__pytra_ensure_local_type_ids_*` helper と `py_tid_register_known_class_type(...)` 呼び出しが消えていることを確認
- `runtime_parity_check_fast.py`:
  - fixture `131/131 PASS`
  - sample `18/18 PASS`
