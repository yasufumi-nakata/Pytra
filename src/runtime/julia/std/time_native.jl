# Native implementation for pytra.std.time
# Generated std/time.jl delegates host bindings through this native seam.

module __TimeNative
    function perf_counter()
        return time()
    end
end
