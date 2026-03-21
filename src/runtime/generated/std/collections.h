// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/std/collections.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_COLLECTIONS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_COLLECTIONS_H

#include "runtime/cpp/core/py_runtime.h"

#include "runtime/cpp/core/exceptions.h"

namespace pytra::std::collections {

struct deque;

    struct deque {
        Object<list<int64>> _items;
        
        deque() {
            this->_items = rc_list_from_value(list<int64>{});
        }
        void append(int64 value) {
            rc_list_ref(this->_items).append(value);
        }
        void appendleft(int64 value) {
            this->_items.insert(0, value);
        }
        int64 pop() const {
            if ((rc_list_ref(this->_items)).empty())
                throw IndexError("pop from empty deque");
            return rc_list_ref(this->_items).pop();
        }
        int64 popleft() {
            if ((rc_list_ref(this->_items)).empty())
                throw IndexError("pop from empty deque");
            int64 item = py_list_at_ref(rc_list_ref(this->_items), 0);
            this->_items = rc_list_from_value(py_list_slice_copy(rc_list_ref(this->_items), 1, int64(rc_list_ref(this->_items).size())));
            return item;
        }
        int64 __len__() const {
            return (rc_list_ref(this->_items)).size();
        }
        void clear() {
            this->_items = object(make_object<list<object>>(PYTRA_TID_LIST, list<object>{}));
        }
    };


}  // namespace pytra::std::collections

using namespace pytra::std::collections;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_COLLECTIONS_H
