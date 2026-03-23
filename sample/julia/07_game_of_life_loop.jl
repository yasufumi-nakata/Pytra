include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 07: Sample that outputs Game of Life evolution as a GIF.

function next_state(grid, w, h)
    nxt = Any[]
    for y in 0:h - 1
        row = Any[]
        for x in 0:w - 1
            cnt = 0
            for dy in (-1):2 - 1
                for dx in (-1):2 - 1
                    if ((dx != 0) || (dy != 0))
                        nx = (((x + dx) + w) % w)
                        ny = (((y + dy) + h) % h)
                        cnt = cnt + grid[__pytra_idx(ny, length(grid))][__pytra_idx(nx, length(grid[__pytra_idx(ny, length(grid))]))]
                    end
                end
            end
            alive = grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))]
            if ((alive == 1) && ((cnt == 2) || (cnt == 3)))
                push!(row, 1)
            elseif ((alive == 0) && (cnt == 3))
                push!(row, 1)
            else
                push!(row, 0)
            end
        end
        push!(nxt, row)
    end
    return nxt
end

function render(grid, w, h, cell)
    width = (w * cell)
    height = (h * cell)
    frame = __pytra_bytearray((width * height))
    for y in 0:h - 1
        for x in 0:w - 1
            v = (__pytra_truthy(grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))]) ? (255) : (0))
            for yy in 0:cell - 1
                base = ((((y * cell) + yy) * width) + (x * cell))
                for xx in 0:cell - 1
                    frame[__pytra_idx((base + xx), length(frame))] = v
                end
            end
        end
    end
    return __pytra_bytes(frame)
end

function run_07_game_of_life_loop()
    w = 144
    h = 108
    cell = 4
    steps = 105
    out_path = "sample/out/07_game_of_life_loop.gif"
    
    start = perf_counter()
    grid = Any[]
    for _ in 0:h - 1
        push!(grid, __pytra_repeat_seq([0], w))
    end
    
    # Lay down sparse noise so the whole field is less likely to stabilize too early.
    # Avoid large integer literals so all transpilers handle the expression consistently.
    for y in 0:h - 1
        for x in 0:w - 1
            noise = (((((x * 37) + (y * 73)) + ((x * y) % 19)) + ((x + y) % 11)) % 97)
            if (noise < 3)
                grid[__pytra_idx(y, length(grid))][__pytra_idx(x, length(grid[__pytra_idx(y, length(grid))]))] = 1
            end
        end
    end
    # Place multiple well-known long-lived patterns.
    glider = [[0, 1, 0], [0, 0, 1], [1, 1, 1]]
    r_pentomino = [[0, 1, 1], [1, 1, 0], [0, 1, 0]]
    lwss = [[0, 1, 1, 1, 1], [1, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 0, 0, 1, 0]]
    
    for gy in 8:18:((h - 8)) - 1
        for gx in 8:22:((w - 8)) - 1
            kind = (((gx * 7) + (gy * 11)) % 3)
            ph = nothing
            pw = nothing
            px = nothing
            py = nothing
            if (kind == 0)
                ph = length(glider)
                for py in 0:ph - 1
                    pw = length(glider[__pytra_idx(py, length(glider))])
                    for px in 0:pw - 1
                        if (glider[__pytra_idx(py, length(glider))][__pytra_idx(px, length(glider[__pytra_idx(py, length(glider))]))] == 1)
                            grid[__pytra_idx(((gy + py) % h), length(grid))][__pytra_idx(((gx + px) % w), length(grid[__pytra_idx(((gy + py) % h), length(grid))]))] = 1
                        end
                    end
                end
            elseif (kind == 1)
                ph = length(r_pentomino)
                for py in 0:ph - 1
                    pw = length(r_pentomino[__pytra_idx(py, length(r_pentomino))])
                    for px in 0:pw - 1
                        if (r_pentomino[__pytra_idx(py, length(r_pentomino))][__pytra_idx(px, length(r_pentomino[__pytra_idx(py, length(r_pentomino))]))] == 1)
                            grid[__pytra_idx(((gy + py) % h), length(grid))][__pytra_idx(((gx + px) % w), length(grid[__pytra_idx(((gy + py) % h), length(grid))]))] = 1
                        end
                    end
                end
            else
                ph = length(lwss)
                for py in 0:ph - 1
                    pw = length(lwss[__pytra_idx(py, length(lwss))])
                    for px in 0:pw - 1
                        if (lwss[__pytra_idx(py, length(lwss))][__pytra_idx(px, length(lwss[__pytra_idx(py, length(lwss))]))] == 1)
                            grid[__pytra_idx(((gy + py) % h), length(grid))][__pytra_idx(((gx + px) % w), length(grid[__pytra_idx(((gy + py) % h), length(grid))]))] = 1
                        end
                    end
                end
            end
        end
    end
    frames = Any[]
    for _ in 0:steps - 1
        push!(frames, render(grid, w, h, cell))
        grid = next_state(grid, w, h)
    end
    save_gif(out_path, (w * cell), (h * cell), frames, grayscale_palette(), 4, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", steps)
    __pytra_print("elapsed_sec:", elapsed)
end


run_07_game_of_life_loop();
