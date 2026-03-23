include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 13: Sample that outputs DFS maze-generation progress as a GIF.

function capture(grid, w, h, scale)
    width = (w * scale)
    height = (h * scale)
    frame = __pytra_bytearray((width * height))
    for y in 0:h - 1
        for x in 0:w - 1
            v = (__pytra_truthy((grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))] == 0)) ? (255) : (40))
            for yy in 0:scale - 1
                base = ((((y * scale) + yy) * width) + (x * scale))
                for xx in 0:scale - 1
                    frame[__pytra_idx((base + xx), length(frame))] = v
                end
            end
        end
    end
    return __pytra_bytes(frame)
end

function run_13_maze_generation_steps()
    # Increase maze size and render resolution to ensure sufficient runtime.
    cell_w = 89
    cell_h = 67
    scale = 5
    capture_every = 20
    out_path = "sample/out/13_maze_generation_steps.gif"
    
    start = perf_counter()
    grid = Any[]
    for _ in 0:cell_h - 1
        push!(grid, __pytra_repeat_seq([1], cell_w))
    end
    stack = [(1, 1)]
    grid[2][2] = 0
    
    dirs = [(2, 0), ((-2), 0), (0, 2), (0, (-2))]
    frames = Any[]
    step_ = 0
    
    while __pytra_truthy(stack)
        (x, y) = stack[end + 0]
        candidates = Any[]
        nx = nothing
        ny = nothing
        for k in 0:4 - 1
            (dx, dy) = dirs[__pytra_idx(k, length(dirs))]
            nx = (x + dx)
            ny = (y + dy)
            if ((nx >= 1) && (nx < (cell_w - 1)) && (ny >= 1) && (ny < (cell_h - 1)) && (grid[__pytra_idx(ny, length(grid))][__pytra_idx(nx, length(grid[__pytra_idx(ny, length(grid))]))] == 1))
                if (dx == 2)
                    push!(candidates, (nx, ny, (x + 1), y))
                elseif (dx == (-2))
                    push!(candidates, (nx, ny, (x - 1), y))
                else
                    if (dy == 2)
                        push!(candidates, (nx, ny, x, (y + 1)))
                    else
                        push!(candidates, (nx, ny, x, (y - 1)))
                    end
                end
            end
        end
        if (length(candidates) == 0)
            pop!(stack)
        else
            sel = candidates[__pytra_idx(((((x * 17) + (y * 29)) + (length(stack) * 13)) % length(candidates)), length(candidates))]
            (nx, ny, wx, wy) = sel
            grid[__pytra_idx(wy, length(grid))][__pytra_idx(wx, length(grid[__pytra_idx(wy, length(grid))]))] = 0
            grid[__pytra_idx(ny, length(grid))][__pytra_idx(nx, length(grid[__pytra_idx(ny, length(grid))]))] = 0
            push!(stack, (nx, ny))
        end
        if ((step_ % capture_every) == 0)
            push!(frames, capture(grid, cell_w, cell_h, scale))
        end
        step_ = step_ + 1
    end
    push!(frames, capture(grid, cell_w, cell_h, scale))
    save_gif(out_path, (cell_w * scale), (cell_h * scale), frames, grayscale_palette(), 4, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", length(frames))
    __pytra_print("elapsed_sec:", elapsed)
end


run_13_maze_generation_steps();
