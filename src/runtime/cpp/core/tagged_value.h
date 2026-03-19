#ifndef PYTRA_CORE_TAGGED_VALUE_H
#define PYTRA_CORE_TAGGED_VALUE_H

#include "core/py_types.h"

// PyBoxed<T, TID>: box any value type into an RcObject for object storage.
template <class T, pytra_type_id TID>
struct PyBoxed : RcObject {
    T value;
    PyBoxed() : value() {}
    explicit PyBoxed(const T& v) : value(v) {}
    pytra_type_id py_type_id() const noexcept override { return TID; }
};

// py_box / py_unbox: standalone helpers (prefer object::unbox in new code).
template <class T, pytra_type_id TID>
static inline object py_box(const T& v) {
    return object(static_cast<RcObject*>(new PyBoxed<T, TID>(v)));
}

template <class T, pytra_type_id TID>
static inline const T& py_unbox(const object& v) {
    return static_cast<PyBoxed<T, TID>*>(v.get())->value;
}

// Deferred object POD constructors (str is now complete).
inline object::object(const str& v) : tag(PYTRA_TID_STR), _rc(static_cast<RcObject*>(new PyBoxed<str, PYTRA_TID_STR>(v))) {}
inline object::object(const char* v) : tag(PYTRA_TID_STR), _rc(static_cast<RcObject*>(new PyBoxed<str, PYTRA_TID_STR>(str(v)))) {}
inline object::object(int64 v) : tag(PYTRA_TID_INT), _rc(static_cast<RcObject*>(new PyBoxed<int64, PYTRA_TID_INT>(v))) {}
inline object::object(int v) : tag(PYTRA_TID_INT), _rc(static_cast<RcObject*>(new PyBoxed<int64, PYTRA_TID_INT>(static_cast<int64>(v)))) {}
inline object::object(float64 v) : tag(PYTRA_TID_FLOAT), _rc(static_cast<RcObject*>(new PyBoxed<float64, PYTRA_TID_FLOAT>(v))) {}
inline object::object(bool v) : tag(PYTRA_TID_BOOL), _rc(static_cast<RcObject*>(new PyBoxed<bool, PYTRA_TID_BOOL>(v))) {}

// Backward-compat shims for old object API (to be removed).
template <class T>
static inline object make_object(const T& v) { return object(v); }

template <class T>
static inline object make_object(const rc<T>& v) { return object(v); }

template <class T>
static inline rc<T> obj_to_rc_or_raise(const object& v, const char* ctx) {
    (void)ctx;
    T* raw = static_cast<T*>(v.get());
    if (!raw) throw ::std::runtime_error("obj_to_rc_or_raise: null");
    raw->rc_retain();
    return rc<T>::adopt(raw);
}

#endif  // PYTRA_CORE_TAGGED_VALUE_H
