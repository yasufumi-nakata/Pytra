#include "core/py_runtime.h"
#include "core/process_runtime.h"

namespace pytra::built_in::zip_ops {

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
    
}  // namespace pytra::built_in::zip_ops
