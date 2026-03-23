include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "math.jl"))
math = (ceil=ceil, cos=cos, e=e, exp=exp, fabs=fabs, floor=floor, log=log, log10=log10, pi=pi, pow=pow, sin=sin, sqrt=sqrt, tan=tan)
include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 14: Sample that outputs a moving-light scene in a simple raymarching style as a GIF.

function palette()
    p = UInt8[]
    for i in 0:256 - 1
        r = min(255, __pytra_int((20 + (i * 0.9))))
        g = min(255, __pytra_int((10 + (i * 0.7))))
        b = min(255, (30 + i))
        push!(p, r)
        push!(p, g)
        push!(p, b)
    end
    return __pytra_bytes(p)
end

function scene(x, y, light_x, light_y)
    x1 = (x + 0.45)
    y1 = (y + 0.2)
    x2 = (x - 0.35)
    y2 = (y - 0.15)
    r1 = math.sqrt(((x1 * x1) + (y1 * y1)))
    r2 = math.sqrt(((x2 * x2) + (y2 * y2)))
    blob = (math.exp((((-7.0) * r1) * r1)) + math.exp((((-8.0) * r2) * r2)))
    
    lx = (x - light_x)
    ly = (y - light_y)
    l = math.sqrt(((lx * lx) + (ly * ly)))
    lit = (1.0 / (1.0 + ((3.5 * l) * l)))
    
    v = __pytra_int((((255.0 * blob) * lit) * 5.0))
    return min(255, max(0, v))
end

function run_14_raymarching_light_cycle()
    w = 320
    h = 240
    frames_n = 84
    out_path = "sample/out/14_raymarching_light_cycle.gif"
    
    start = perf_counter()
    frames = Any[]
    
    for t in 0:frames_n - 1
        frame = __pytra_bytearray((w * h))
        a = (((t / frames_n) * math.pi) * 2.0)
        light_x = (0.75 * math.cos(a))
        light_y = (0.55 * math.sin((a * 1.2)))
        
        for y in 0:h - 1
            row_base = (y * w)
            py = (((y / (h - 1)) * 2.0) - 1.0)
            for x in 0:w - 1
                px = (((x / (w - 1)) * 2.0) - 1.0)
                frame[__pytra_idx((row_base + x), length(frame))] = scene(px, py, light_x, light_y)
            end
        end
        push!(frames, __pytra_bytes(frame))
    end
    save_gif(out_path, w, h, frames, palette(), 3, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
end


run_14_raymarching_light_cycle();
