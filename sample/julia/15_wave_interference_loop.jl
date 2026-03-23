include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "math.jl"))
math = (ceil=ceil, cos=cos, e=e, exp=exp, fabs=fabs, floor=floor, log=log, log10=log10, pi=pi, pow=pow, sin=sin, sqrt=sqrt, tan=tan)
include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 15: Sample that renders wave interference animation and writes a GIF.

function run_15_wave_interference_loop()
    w = 320
    h = 240
    frames_n = 96
    out_path = "sample/out/15_wave_interference_loop.gif"
    
    start = perf_counter()
    frames = Any[]
    
    for t in 0:frames_n - 1
        frame = __pytra_bytearray((w * h))
        phase = (t * 0.12)
        for y in 0:h - 1
            row_base = (y * w)
            for x in 0:w - 1
                dx = (x - 160)
                dy = (y - 120)
                v = (((math.sin(((x + (t * 1.5)) * 0.045)) + math.sin(((y - (t * 1.2)) * 0.04))) + math.sin((((x + y) * 0.02) + phase))) + math.sin(((math.sqrt(((dx * dx) + (dy * dy))) * 0.08) - (phase * 1.3))))
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
    save_gif(out_path, w, h, frames, grayscale_palette(), 4, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
end


run_15_wave_interference_loop();
