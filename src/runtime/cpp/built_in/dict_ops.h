#ifndef PYTRA_BUILT_IN_DICT_OPS_H
#define PYTRA_BUILT_IN_DICT_OPS_H

#include <stdexcept>
#include "core/py_types.h"

template <class K, class V, class Q>
static inline V& py_at(dict<K, V>& d, const Q& key) {
    const K k = [&]() -> K {
        if constexpr (py_is_cstr_like<Q>::value) {
            return py_coerce_cstr_typed_value<K>(key);
        } else if constexpr (::std::is_same_v<K, Q>) {
            return key;
        } else if constexpr (::std::is_convertible_v<Q, K>) {
            return static_cast<K>(key);
        } else {
            return K(key);
        }
    }();
    auto it = d.find(k);
    if (it == d.end()) {
        throw ::std::out_of_range("dict key not found");
    }
    return it->second;
}

template <class K, class V, class Q>
static inline const V& py_at(const dict<K, V>& d, const Q& key) {
    const K k = [&]() -> K {
        if constexpr (py_is_cstr_like<Q>::value) {
            return py_coerce_cstr_typed_value<K>(key);
        } else if constexpr (::std::is_same_v<K, Q>) {
            return key;
        } else if constexpr (::std::is_convertible_v<Q, K>) {
            return static_cast<K>(key);
        } else {
            return K(key);
        }
    }();
    auto it = d.find(k);
    if (it == d.end()) {
        throw ::std::out_of_range("dict key not found");
    }
    return it->second;
}

template <class K, class V, class Q, class D>
static inline V py_dict_get(const dict<K, V>& d, const Q& key, const D& default_value) {
    const K k = [&]() -> K {
        if constexpr (py_is_cstr_like<Q>::value) {
            return py_coerce_cstr_typed_value<K>(key);
        } else if constexpr (::std::is_same_v<K, Q>) {
            return key;
        } else if constexpr (::std::is_convertible_v<Q, K>) {
            return static_cast<K>(key);
        } else {
            return K(key);
        }
    }();
    auto it = d.find(k);
    if (it != d.end()) {
        return it->second;
    }
    if constexpr (::std::is_same_v<V, D>) {
        return default_value;
    } else if constexpr (::std::is_convertible_v<D, V>) {
        return static_cast<V>(default_value);
    } else {
        return V(default_value);
    }
}

template <class T>
static inline int64 py_index(const list<T>& v, const T& item) {
    return v.index(item);
}

#endif  // PYTRA_BUILT_IN_DICT_OPS_H

// py_at for tuple (runtime index → object conversion)
template <class... Ts>
static inline object py_at(const ::std::tuple<Ts...>& t, int64 idx) {
    object result;
    int64 cur = 0;
    ::std::apply([&](const auto&... args) {
        ((cur++ == idx ? (result = object(args), true) : false) || ...);
    }, t);
    return result;
}

template <class... Ts>
static inline object py_at(const ::std::tuple<Ts...>& t, int idx) {
    return py_at(t, static_cast<int64>(idx));
}
