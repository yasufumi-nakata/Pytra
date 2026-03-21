// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/built_in/iter_ops.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_ITER_OPS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_ITER_OPS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::built_in::iter_ops {

list<object> py_reversed_object(const object& values);
list<object> py_enumerate_object(const object& values, int64 start = 0);

}  // namespace pytra::built_in::iter_ops

using namespace pytra::built_in::iter_ops;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_ITER_OPS_H
