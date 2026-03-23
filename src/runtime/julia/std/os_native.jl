# Native implementation for pytra.std.os
# Generated std/os.jl delegates host bindings through this native seam.

module __OsNative
    function getcwd()
        return pwd()
    end
    function mkdir(path, exist_ok)
        if exist_ok && isdir(path)
            return nothing
        end
        Base.mkdir(path)
        return nothing
    end
    function makedirs(path, exist_ok)
        if exist_ok && isdir(path)
            return nothing
        end
        Base.mkpath(path)
        return nothing
    end
end
