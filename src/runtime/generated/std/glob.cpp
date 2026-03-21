#include "core/py_runtime.h"
#include "core/process_runtime.h"

namespace pytra::std::glob {

    /* pytra.std.glob: extern-marked glob subset with Python runtime fallback. */
    
    Object<list<str>> glob(const str& pattern) {
        return py_to<Object<list<str>>>(_glob_mod.glob(pattern));
    }
    
}  // namespace pytra::std::glob
