include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "math.jl"))
math = (ceil=ceil, cos=cos, e=e, exp=exp, fabs=fabs, floor=floor, log=log, log10=log10, pi=pi, pow=pow, sin=sin, sqrt=sqrt, tan=tan)
include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 11: Sample that outputs Lissajous-motion particles as a GIF.

function color_palette()
    p = UInt8[]
    for i in 0:256 - 1
        r = i
        g = ((i * 3) % 256)
        b = (255 - i)
        push!(p, r)
        push!(p, g)
        push!(p, b)
    end
    return __pytra_bytes(p)
end

function run_11_lissajous_particles()
    w = 320
    h = 240
    frames_n = 360
    particles = 48
    out_path = "sample/out/11_lissajous_particles.gif"
    
    start = perf_counter()
    frames = Any[]
    
    for t in 0:frames_n - 1
        frame = __pytra_bytearray((w * h))
        
        for p in 0:particles - 1
            phase = (p * 0.261799)
            x = __pytra_int(((w * 0.5) + ((w * 0.38) * math.sin(((0.11 * t) + (phase * 2.0))))))
            y = __pytra_int(((h * 0.5) + ((h * 0.38) * math.sin(((0.17 * t) + (phase * 3.0))))))
            color = (30 + ((p * 9) % 220))
            
            for dy in (-2):3 - 1
                for dx in (-2):3 - 1
                    xx = (x + dx)
                    yy = (y + dy)
                    if ((xx >= 0) && (xx < w) && (yy >= 0) && (yy < h))
                        d2 = ((dx * dx) + (dy * dy))
                        if (d2 <= 4)
                            idx = ((yy * w) + xx)
                            v = (color - (d2 * 20))
                            v = max(0, v)
                            if (v > frame[__pytra_idx(idx, length(frame))])
                                frame[__pytra_idx(idx, length(frame))] = v
                            end
                        end
                    end
                end
            end
        end
        push!(frames, __pytra_bytes(frame))
    end
    save_gif(out_path, w, h, frames, color_palette(), 3, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
end


run_11_lissajous_particles();
