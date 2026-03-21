// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/utils/assertions.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_UTILS_ASSERTIONS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_UTILS_ASSERTIONS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::utils::assertions {

struct _Union_str_int64_float64_bool_None {
    pytra_type_id tag;
    str str_val;
    int64 int64_val;
    float64 float64_val;
    bool bool_val;

    _Union_str_int64_float64_bool_None() : tag(PYTRA_TID_NONE) {}
    _Union_str_int64_float64_bool_None(const str& v) : tag(PYTRA_TID_STR), str_val(v) {}
    _Union_str_int64_float64_bool_None(const int64& v) : tag(PYTRA_TID_INT), int64_val(v) {}
    _Union_str_int64_float64_bool_None(const float64& v) : tag(PYTRA_TID_FLOAT), float64_val(v) {}
    _Union_str_int64_float64_bool_None(const bool& v) : tag(PYTRA_TID_BOOL), bool_val(v) {}
    _Union_str_int64_float64_bool_None(::std::monostate) : tag(PYTRA_TID_NONE) {}
};


bool _eq_any(const _Union_str_int64_float64_bool_None& actual, const _Union_str_int64_float64_bool_None& expected);
bool py_assert_true(bool cond, const str& label = "");
bool py_assert_eq(const _Union_str_int64_float64_bool_None& actual, const _Union_str_int64_float64_bool_None& expected, const str& label = "");
bool py_assert_all(const list<bool>& results, const str& label = "");
bool py_assert_stdout(const list<str>& expected_lines, const object& fn);

}  // namespace pytra::utils::assertions

using namespace pytra::utils::assertions;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_UTILS_ASSERTIONS_H
