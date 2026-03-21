-- Generated std/time.lua delegates host bindings through this native seam.
-- source: src/runtime/cs/std/time_native.cs (reference)

local time_native = {}

function time_native.perf_counter()
    return os.clock()
end

return time_native
