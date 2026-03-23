include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "png.jl"))
png = (_adler32=_adler32, _chunk=_chunk, _crc32=_crc32, _png_append_list=_png_append_list, _png_u16le=_png_u16le, _png_u32be=_png_u32be, _zlib_deflate_store=_zlib_deflate_store, write_rgb_png=write_rgb_png)

# 01: Sample that outputs the Mandelbrot set as a PNG image.
# Syntax is kept straightforward with future transpilation in mind.

function escape_count(cx, cy, max_iter)
    x = 0.0
    y = 0.0
    for i in 0:max_iter - 1
        x2 = (x * x)
        y2 = (y * y)
        if ((x2 + y2) > 4.0)
            return i
        end
        y = (((2.0 * x) * y) + cy)
        x = ((x2 - y2) + cx)
    end
    return max_iter
end

function color_map(iter_count, max_iter)
    if (iter_count >= max_iter)
        return (0, 0, 0)
    end
    t = (iter_count / max_iter)
    r = __pytra_int((255.0 * (t * t)))
    g = __pytra_int((255.0 * t))
    b = __pytra_int((255.0 * (1.0 - t)))
    return (r, g, b)
end

function render_mandelbrot(width, height, max_iter, x_min, x_max, y_min, y_max)
    pixels = UInt8[]
    
    for y in 0:height - 1
        py = (y_min + ((y_max - y_min) * (y / (height - 1))))
        
        for x in 0:width - 1
            px = (x_min + ((x_max - x_min) * (x / (width - 1))))
            it = escape_count(px, py, max_iter)
            r = nothing
            g = nothing
            b = nothing
            if (it >= max_iter)
                r = 0
                g = 0
                b = 0
            else
                t = (it / max_iter)
                r = __pytra_int((255.0 * (t * t)))
                g = __pytra_int((255.0 * t))
                b = __pytra_int((255.0 * (1.0 - t)))
            end
            push!(pixels, r)
            push!(pixels, g)
            push!(pixels, b)
        end
    end
    return pixels
end

function run_mandelbrot()
    width = 1600
    height = 1200
    max_iter = 1000
    out_path = "sample/out/01_mandelbrot.png"
    
    start = perf_counter()
    
    pixels = render_mandelbrot(width, height, max_iter, (-2.2), 1.0, (-1.2), 1.2)
    png.write_rgb_png(out_path, width, height, pixels)
    
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("size:", width, "x", height)
    __pytra_print("max_iter:", max_iter)
    __pytra_print("elapsed_sec:", elapsed)
end


run_mandelbrot();
