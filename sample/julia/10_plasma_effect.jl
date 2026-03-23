include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "math.jl"))
math = (ceil=ceil, cos=cos, e=e, exp=exp, fabs=fabs, floor=floor, log=log, log10=log10, pi=pi, pow=pow, sin=sin, sqrt=sqrt, tan=tan)
include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 10: Sample that outputs a plasma effect as a GIF.

function run_10_plasma_effect()
    w = 320
    h = 240
    frames_n = 216
    out_path = "sample/out/10_plasma_effect.gif"
    
    start = perf_counter()
    frames = Any[]
    
    for t in 0:frames_n - 1
        frame = __pytra_bytearray((w * h))
        for y in 0:h - 1
            row_base = (y * w)
            for x in 0:w - 1
                dx = (x - 160)
                dy = (y - 120)
                v = (((math.sin(((x + (t * 2.0)) * 0.045)) + math.sin(((y - (t * 1.2)) * 0.05))) + math.sin((((x + y) + (t * 1.7)) * 0.03))) + math.sin(((math.sqrt(((dx * dx) + (dy * dy))) * 0.07) - (t * 0.18))))
                c = __pytra_int(((v + 4.0) * (255.0 / 8.0)))
                if (c < 0)
                    c = 0
                end
                if (c > 255)
                    c = 255
                end
                frame[__pytra_idx((row_base + x), length(frame))] = c
            end
        end
        push!(frames, __pytra_bytes(frame))
    end
    save_gif(out_path, w, h, frames, grayscale_palette(), 3, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
end


run_10_plasma_effect();
