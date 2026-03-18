// AUTO-GENERATED FILE. DO NOT EDIT.
#include "pytra_multi_prelude.h"
#include "utils_assertions_cpp_object_iter_helper.h"

namespace pytra_multi_helper {
object object_iter_or_raise(const object& value) {
    object __obj = value;
    if (!__obj) throw TypeError("NoneType is not iterable");
    return __obj->py_iter_or_raise();
}

::std::optional<object> object_iter_next_or_stop(const object& iter_obj) {
    object __iter = iter_obj;
    if (!__iter) throw TypeError("NoneType is not an iterator");
    return __iter->py_next_or_stop();
}
}  // namespace pytra_multi_helper
