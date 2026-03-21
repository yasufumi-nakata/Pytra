// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/built_in/contains.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_CONTAINS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_CONTAINS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::built_in::contains {

bool py_contains_dict_object(const object& values, const object& key);
bool py_contains_list_object(const object& values, const object& key);
bool py_contains_set_object(const object& values, const object& key);
bool py_contains_str_object(const object& values, const object& key);

}  // namespace pytra::built_in::contains

using namespace pytra::built_in::contains;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_BUILT_IN_CONTAINS_H
