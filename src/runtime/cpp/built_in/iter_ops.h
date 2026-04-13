#ifndef PYTRA_NATIVE_BUILT_IN_ITER_OPS_H
#define PYTRA_NATIVE_BUILT_IN_ITER_OPS_H

#include "built_in/iter_ops.h"

static inline list<int64> py_range(int64 stop) {
    list<int64> out;
    if (stop <= 0) return out;
    out.reserve(static_cast<::std::size_t>(stop));
    for (int64 i = 0; i < stop; ++i) {
        out.append(i);
    }
    return out;
}

static inline list<int64> py_range(int64 start, int64 stop, int64 step) {
    list<int64> out;
    if (step == 0) {
        throw ::std::runtime_error("range() arg 3 must not be zero");
    }
    if (step > 0) {
        for (int64 i = start; i < stop; i += step) {
            out.append(i);
        }
        return out;
    }
    for (int64 i = start; i > stop; i += step) {
        out.append(i);
    }
    return out;
}

template <class T>
static inline list<T> py_reversed_list_copy(const list<T>& values) {
    list<T> out(values.begin(), values.end());
    ::std::reverse(out.begin(), out.end());
    return out;
}

template <class T>
static inline list<T> py_reversed(const list<T>& values) {
    return py_reversed_list_copy(values);
}

template <class T>
static inline list<T> py_reversed(const Object<list<T>>& values) {
    return py_reversed_list_copy(*values);
}

template <class T>
static inline list<T> py_reversed_object(const list<T>& values) {
    return py_reversed_list_copy(values);
}

template <class T>
static inline list<T> py_reversed_object(const Object<list<T>>& values) {
    return py_reversed_list_copy(*values);
}

template <class T>
static inline list<::std::tuple<int64, T>> py_enumerate_list_copy(const list<T>& values, int64 start) {
    list<::std::tuple<int64, T>> out;
    out.reserve(values.size());
    for (::std::size_t i = 0; i < values.size(); i++) {
        out.append(::std::make_tuple(start + static_cast<int64>(i), values[i]));
    }
    return out;
}

template <class T>
static inline list<::std::tuple<int64, T>> py_enumerate(const list<T>& values) {
    return py_enumerate_list_copy(values, 0);
}

template <class T>
static inline list<::std::tuple<int64, T>> py_enumerate(const list<T>& values, int64 start) {
    return py_enumerate_list_copy(values, start);
}

template <class T>
static inline list<::std::tuple<int64, T>> py_enumerate(const Object<list<T>>& values) {
    return py_enumerate_list_copy(*values, 0);
}

template <class T>
static inline list<::std::tuple<int64, T>> py_enumerate(const Object<list<T>>& values, int64 start) {
    return py_enumerate_list_copy(*values, start);
}

static inline list<::std::tuple<int64, str>> py_enumerate(const str& values) {
    list<::std::tuple<int64, str>> out;
    out.reserve(values.size());
    for (::std::size_t i = 0; i < values.size(); i++) {
        out.append(::std::make_tuple(static_cast<int64>(i), values[i]));
    }
    return out;
}

static inline list<::std::tuple<int64, str>> py_enumerate(const str& values, int64 start) {
    list<::std::tuple<int64, str>> out;
    out.reserve(values.size());
    for (::std::size_t i = 0; i < values.size(); i++) {
        out.append(::std::make_tuple(start + static_cast<int64>(i), values[i]));
    }
    return out;
}

#endif  // PYTRA_NATIVE_BUILT_IN_ITER_OPS_H
