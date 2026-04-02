#ifndef PYTRA_NATIVE_BUILT_IN_SET_OPS_H
#define PYTRA_NATIVE_BUILT_IN_SET_OPS_H

#include "core/py_types.h"

template <class T, class U>
static inline void py_set_add_mut(set<T>& values, const U& item) {
    if constexpr (::std::is_same_v<T, U>) {
        values.add(item);
    } else if constexpr (::std::is_convertible_v<U, T>) {
        values.add(static_cast<T>(item));
    } else {
        values.add(T(item));
    }
}

template <class T, class U>
static inline void py_set_add_mut(Object<set<T>>& values, const U& item) {
    py_set_add_mut(*values, item);
}

template <class T, class U>
static inline void py_set_discard_mut(set<T>& values, const U& item) {
    if constexpr (::std::is_same_v<T, U>) {
        values.discard(item);
    } else if constexpr (::std::is_convertible_v<U, T>) {
        values.discard(static_cast<T>(item));
    } else {
        values.discard(T(item));
    }
}

template <class T, class U>
static inline void py_set_discard_mut(Object<set<T>>& values, const U& item) {
    py_set_discard_mut(*values, item);
}

template <class T, class U>
static inline void py_set_remove_mut(set<T>& values, const U& item) {
    if constexpr (::std::is_same_v<T, U>) {
        values.remove(item);
    } else if constexpr (::std::is_convertible_v<U, T>) {
        values.remove(static_cast<T>(item));
    } else {
        values.remove(T(item));
    }
}

template <class T, class U>
static inline void py_set_remove_mut(Object<set<T>>& values, const U& item) {
    py_set_remove_mut(*values, item);
}

template <class T>
static inline void py_set_clear_mut(set<T>& values) {
    values.clear();
}

template <class T>
static inline void py_set_clear_mut(Object<set<T>>& values) {
    py_set_clear_mut(*values);
}

#endif  // PYTRA_NATIVE_BUILT_IN_SET_OPS_H
