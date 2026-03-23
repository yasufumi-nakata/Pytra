# Native implementation for pytra.std.math
# Generated std/math.jl delegates host bindings through this native seam.

module __MathNative
    const pi = Float64(Base.MathConstants.pi)
    const e = Float64(Base.MathConstants.e)

    function sqrt(x)
        return Base.sqrt(x)
    end
    function sin(x)
        return Base.sin(x)
    end
    function cos(x)
        return Base.cos(x)
    end
    function tan(x)
        return Base.tan(x)
    end
    function exp(x)
        return Base.exp(x)
    end
    function log(x)
        return Base.log(x)
    end
    function log10(x)
        return Base.log10(x)
    end
    function fabs(x)
        return Base.abs(x)
    end
    function floor(x)
        return Int(Base.floor(x))
    end
    function ceil(x)
        return Int(Base.ceil(x))
    end
    function pow(b, e)
        return b ^ e
    end
end
