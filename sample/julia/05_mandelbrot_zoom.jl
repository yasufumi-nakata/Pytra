include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 05: Sample that outputs a Mandelbrot zoom as an animated GIF.

function render_frame(width, height, center_x, center_y, scale, max_iter)
    frame = __pytra_bytearray((width * height))
    for y in 0:height - 1
        row_base = (y * width)
        cy = (center_y + ((y - (height * 0.5)) * scale))
        for x in 0:width - 1
            cx = (center_x + ((x - (width * 0.5)) * scale))
            zx = 0.0
            zy = 0.0
            i = 0
            while (i < max_iter)
                zx2 = (zx * zx)
                zy2 = (zy * zy)
                if ((zx2 + zy2) > 4.0)
                    break
                end
                zy = (((2.0 * zx) * zy) + cy)
                zx = ((zx2 - zy2) + cx)
                i = i + 1
            end
            frame[__pytra_idx((row_base + x), length(frame))] = __pytra_int(((255.0 * i) / max_iter))
        end
    end
    return __pytra_bytes(frame)
end

function run_05_mandelbrot_zoom()
    width = 320
    height = 240
    frame_count = 48
    max_iter = 110
    center_x = (-0.743643887037151)
    center_y = 0.13182590420533
    base_scale = (3.2 / width)
    zoom_per_frame = 0.93
    out_path = "sample/out/05_mandelbrot_zoom.gif"
    
    start = perf_counter()
    frames = Any[]
    scale = base_scale
    for _ in 0:frame_count - 1
        push!(frames, render_frame(width, height, center_x, center_y, scale, max_iter))
        scale = scale * zoom_per_frame
    end
    save_gif(out_path, width, height, frames, grayscale_palette(), 5, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frame_count)
    __pytra_print("elapsed_sec:", elapsed)
end


run_05_mandelbrot_zoom();
