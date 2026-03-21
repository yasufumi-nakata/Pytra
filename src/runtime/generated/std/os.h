// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/std/os.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_OS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_OS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::std::os {

str getcwd();
void mkdir(const str& p);
void makedirs(const str& p, bool exist_ok = false);

}  // namespace pytra::std::os

using namespace pytra::std::os;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_OS_H
