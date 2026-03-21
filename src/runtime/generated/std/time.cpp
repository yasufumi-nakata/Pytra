#include "core/py_runtime.h"
#include "core/process_runtime.h"

namespace pytra::std::time {

    /* pytra.std.time: extern-marked time API with Python runtime fallback. */
    
    float64 perf_counter() {
        return time.perf_counter();
    }
    
}  // namespace pytra::std::time
