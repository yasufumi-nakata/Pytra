include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 12: Sample that outputs intermediate states of bubble sort as a GIF.

function render(values, w, h)
    frame = __pytra_bytearray((w * h))
    n = length(values)
    bar_w = (w / n)
    for i in 0:n - 1
        x0 = __pytra_int((i * bar_w))
        x1 = __pytra_int(((i + 1) * bar_w))
        if (x1 <= x0)
            x1 = (x0 + 1)
        end
        bh = __pytra_int(((values[__pytra_idx(i, length(values))] / n) * h))
        y = (h - bh)
        for y in y:h - 1
            for x in x0:x1 - 1
                frame[__pytra_idx(((y * w) + x), length(frame))] = 255
            end
        end
    end
    return __pytra_bytes(frame)
end

function run_12_sort_visualizer()
    w = 320
    h = 180
    n = 124
    out_path = "sample/out/12_sort_visualizer.gif"
    
    start = perf_counter()
    values = Any[]
    i = nothing
    for i in 0:n - 1
        push!(values, (((i * 37) + 19) % n))
    end
    frames = [render(values, w, h)]
    frame_stride = 16
    
    op = 0
    for i in 0:n - 1
        swapped = false
        for j in 0:(((n - i) - 1)) - 1
            if (values[__pytra_idx(j, length(values))] > values[__pytra_idx((j + 1), length(values))])
                __swap_tmp_0 = values[__pytra_idx(j, length(values))]
                values[__pytra_idx(j, length(values))] = values[__pytra_idx((j + 1), length(values))]
                values[__pytra_idx((j + 1), length(values))] = __swap_tmp_0
                swapped = true
            end
            if ((op % frame_stride) == 0)
                push!(frames, render(values, w, h))
            end
            op = op + 1
        end
        if (!(swapped))
            break
        end
    end
    save_gif(out_path, w, h, frames, grayscale_palette(), 3, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", length(frames))
    __pytra_print("elapsed_sec:", elapsed)
end


run_12_sort_visualizer();
