// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/built_in/scalar_ops.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_SCALAR_OPS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_SCALAR_OPS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::built_in::scalar_ops {

int64 py_to_int64_base(const str& v, int64 base);
int64 py_ord(const str& ch);
str py_chr(int64 codepoint);

}  // namespace pytra::built_in::scalar_ops

using namespace pytra::built_in::scalar_ops;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_SCALAR_OPS_H
