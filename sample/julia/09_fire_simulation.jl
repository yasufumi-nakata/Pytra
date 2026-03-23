include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 09: Sample that outputs a simple fire effect as a GIF.

function fire_palette()
    p = UInt8[]
    for i in 0:256 - 1
        r = 0
        g = 0
        b = 0
        if (i < 85)
            r = (i * 3)
            g = 0
            b = 0
        elseif (i < 170)
            r = 255
            g = ((i - 85) * 3)
            b = 0
        else
            r = 255
            g = 255
            b = ((i - 170) * 3)
        end
        push!(p, r)
        push!(p, g)
        push!(p, b)
    end
    return __pytra_bytes(p)
end

function run_09_fire_simulation()
    w = 380
    h = 260
    steps = 420
    out_path = "sample/out/09_fire_simulation.gif"
    
    start = perf_counter()
    heat = Any[]
    for _ in 0:h - 1
        push!(heat, __pytra_repeat_seq([0], w))
    end
    frames = Any[]
    
    for t in 0:steps - 1
        x = nothing
        for x in 0:w - 1
            val = (170 + (((x * 13) + (t * 17)) % 86))
            heat[__pytra_idx((h - 1), length(heat))][__pytra_idx(x, length(heat[__pytra_idx((h - 1), length(heat))]))] = val
        end
        for y in 1:h - 1
            for x in 0:w - 1
                a = heat[__pytra_idx(y, length(heat))][__pytra_idx(x, length(heat[__pytra_idx(y, length(heat))]))]
                b = heat[__pytra_idx(y, length(heat))][__pytra_idx((((x - 1) + w) % w), length(heat[__pytra_idx(y, length(heat))]))]
                c = heat[__pytra_idx(y, length(heat))][__pytra_idx(((x + 1) % w), length(heat[__pytra_idx(y, length(heat))]))]
                d = heat[__pytra_idx(((y + 1) % h), length(heat))][__pytra_idx(x, length(heat[__pytra_idx(((y + 1) % h), length(heat))]))]
                v = ((((a + b) + c) + d) ÷ 4)
                cool = (1 + (((x + y) + t) % 3))
                nv = (v - cool)
                heat[__pytra_idx((y - 1), length(heat))][__pytra_idx(x, length(heat[__pytra_idx((y - 1), length(heat))]))] = (__pytra_truthy((nv > 0)) ? (nv) : (0))
            end
        end
        frame = __pytra_bytearray((w * h))
        for yy in 0:h - 1
            row_base = (yy * w)
            for xx in 0:w - 1
                frame[__pytra_idx((row_base + xx), length(frame))] = heat[__pytra_idx(yy, length(heat))][__pytra_idx(xx, length(heat[__pytra_idx(yy, length(heat))]))]
            end
        end
        push!(frames, __pytra_bytes(frame))
    end
    save_gif(out_path, w, h, frames, fire_palette(), 4, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", steps)
    __pytra_print("elapsed_sec:", elapsed)
end


run_09_fire_simulation();
