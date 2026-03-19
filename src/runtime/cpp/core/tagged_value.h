#ifndef PYTRA_CORE_TAGGED_VALUE_H
#define PYTRA_CORE_TAGGED_VALUE_H

#include "core/py_types.h"

// PyBoxed<T, TID>: box any value type into an RcObject for tagged union storage.
template <class T, pytra_type_id TID>
struct PyBoxed : RcObject {
    T value;
    PyBoxed() : value() {}
    explicit PyBoxed(const T& v) : value(v) {}
    pytra_type_id py_type_id() const noexcept override { return TID; }
};

// py_box: wrap a value into object (rc<RcObject>).
template <class T, pytra_type_id TID>
static inline object py_box(const T& v) {
    return object(new PyBoxed<T, TID>(v));
}

// py_unbox: extract the value from a boxed object.
template <class T, pytra_type_id TID>
static inline const T& py_unbox(const object& v) {
    return static_cast<PyBoxed<T, TID>*>(v.get())->value;
}

// PyTaggedValue: universal tagged union representation.
// All tagged unions use this single struct via typedef.
struct PyTaggedValue {
    pytra_type_id tag;
    object value;

    PyTaggedValue() : tag(PYTRA_TID_NONE), value() {}

    // Implicit conversion from POD types (box automatically).
    PyTaggedValue(const str& v) : tag(PYTRA_TID_STR), value(py_box<str, PYTRA_TID_STR>(v)) {}
    PyTaggedValue(const char* v) : tag(PYTRA_TID_STR), value(py_box<str, PYTRA_TID_STR>(str(v))) {}
    PyTaggedValue(int64 v) : tag(PYTRA_TID_INT), value(py_box<int64, PYTRA_TID_INT>(v)) {}
    PyTaggedValue(int v) : tag(PYTRA_TID_INT), value(py_box<int64, PYTRA_TID_INT>(static_cast<int64>(v))) {}
    PyTaggedValue(float64 v) : tag(PYTRA_TID_FLOAT), value(py_box<float64, PYTRA_TID_FLOAT>(v)) {}
    PyTaggedValue(bool v) : tag(PYTRA_TID_BOOL), value(py_box<bool, PYTRA_TID_BOOL>(v)) {}

    // Implicit conversion from rc<T> (class types — upcast to object).
    template <class T, ::std::enable_if_t<::std::is_base_of_v<RcObject, T>, int> = 0>
    PyTaggedValue(const rc<T>& v) : tag(v ? v->py_type_id() : PYTRA_TID_NONE), value(v) {}

    // monostate = None
    PyTaggedValue(::std::monostate) : tag(PYTRA_TID_NONE), value() {}
};

#endif  // PYTRA_CORE_TAGGED_VALUE_H
