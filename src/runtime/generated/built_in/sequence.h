// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/built_in/sequence.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_SEQUENCE_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_SEQUENCE_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::built_in::sequence {

list<int64> py_range(int64 start, int64 stop, int64 step);
str py_repeat(const str& v, int64 n);

}  // namespace pytra::built_in::sequence

using namespace pytra::built_in::sequence;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_SEQUENCE_H
