// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/built_in/numeric_ops.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_NUMERIC_OPS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_NUMERIC_OPS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::built_in::numeric_ops {

T sum(const list<T>& values);
T py_min(const T& a, const T& b);
T py_max(const T& a, const T& b);

}  // namespace pytra::built_in::numeric_ops

using namespace pytra::built_in::numeric_ops;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_NUMERIC_OPS_H
