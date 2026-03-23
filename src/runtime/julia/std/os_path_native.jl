# Native implementation for pytra.std.os_path
# Generated std/os_path.jl delegates host bindings through this native seam.

module __OsPathNative
    function abspath(p)
        return Base.abspath(p)
    end
    function basename(p)
        return Base.basename(p)
    end
    function dirname(p)
        return Base.dirname(p)
    end
    function exists(p)
        return Base.ispath(p)
    end
    function join(parts...)
        return Base.joinpath(parts...)
    end
    function splitext(p)
        root, ext = Base.splitext(p)
        return (root, ext)
    end
end
