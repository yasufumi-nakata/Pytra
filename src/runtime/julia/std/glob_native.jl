# Native implementation for pytra.std.glob
# Generated std/glob.jl delegates host bindings through this native seam.

module __GlobNative
    function glob(pattern)
        return String[f for f in readdir(dirname(pattern) == "" ? "." : dirname(pattern); join=true) if occursin(Regex(replace(replace(basename(pattern), "." => "\\."), "*" => ".*")), basename(f))]
    end
end
