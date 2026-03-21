// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/built_in/zip_ops.py
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA_GENERATED_BUILT_IN_ZIP_OPS_H
#define PYTRA_GENERATED_BUILT_IN_ZIP_OPS_H

#include "core/py_runtime.h"
#include "built_in/sequence.h"

/* Pure-Python source-of-truth for generic zip helpers. */

template <class A, class B>
list<::std::tuple<A, B>> zip(const list<A>& lhs, const list<B>& rhs) {
    Object<list<::std::tuple<A, B>>> out = rc_list_from_value(list<::std::tuple<A, B>>{});
    int64 i = 0;
    int64 n = lhs.size();
    if (rhs.size() < n)
        n = rhs.size();
    while (i < n) {
        rc_list_ref(out).append(::std::make_tuple(lhs[i], rhs[i]));
        i++;
    }
    return rc_list_copy_value(out);
}

#endif  // PYTRA_GENERATED_BUILT_IN_ZIP_OPS_H
