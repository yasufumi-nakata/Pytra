include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 08: Sample that outputs Langton's Ant trajectories as a GIF.

function capture(grid, w, h)
    frame = __pytra_bytearray((w * h))
    for y in 0:h - 1
        row_base = (y * w)
        for x in 0:w - 1
            frame[__pytra_idx((row_base + x), length(frame))] = (__pytra_truthy(grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))]) ? (255) : (0))
        end
    end
    return __pytra_bytes(frame)
end

function run_08_langtons_ant()
    w = 420
    h = 420
    out_path = "sample/out/08_langtons_ant.gif"
    
    start = perf_counter()
    grid = Any[]
    for _ in 0:h - 1
        push!(grid, __pytra_repeat_seq([0], w))
    end
    x = (w ÷ 2)
    y = (h ÷ 2)
    d = 0
    
    steps_total = 600000
    capture_every = 3000
    frames = Any[]
    
    for i in 0:steps_total - 1
        if (grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))] == 0)
            d = ((d + 1) % 4)
            grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))] = 1
        else
            d = ((d + 3) % 4)
            grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))] = 0
        end
        if (d == 0)
            y = (((y - 1) + h) % h)
        elseif (d == 1)
            x = ((x + 1) % w)
        else
            if (d == 2)
                y = ((y + 1) % h)
            else
                x = (((x - 1) + w) % w)
            end
        end
        if ((i % capture_every) == 0)
            push!(frames, capture(grid, w, h))
        end
    end
    save_gif(out_path, w, h, frames, grayscale_palette(), 5, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", length(frames))
    __pytra_print("elapsed_sec:", elapsed)
end


run_08_langtons_ant();
