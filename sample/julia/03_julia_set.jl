include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "png.jl"))
png = (_adler32=_adler32, _chunk=_chunk, _crc32=_crc32, _png_append_list=_png_append_list, _png_u16le=_png_u16le, _png_u32be=_png_u32be, _zlib_deflate_store=_zlib_deflate_store, write_rgb_png=write_rgb_png)

# 03: Sample that outputs a Julia set as a PNG image.
# Implemented with simple loop-centric logic for transpilation compatibility.

function render_julia(width, height, max_iter, cx, cy)
    pixels = UInt8[]
    
    for y in 0:height - 1
        zy0 = ((-1.2) + (2.4 * (y / (height - 1))))
        
        for x in 0:width - 1
            zx = ((-1.8) + (3.6 * (x / (width - 1))))
            zy = zy0
            
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
            r = 0
            g = 0
            b = 0
            if (i >= max_iter)
                r = 0
                g = 0
                b = 0
            else
                t = (i / max_iter)
                r = __pytra_int((255.0 * (0.2 + (0.8 * t))))
                g = __pytra_int((255.0 * (0.1 + (0.9 * (t * t)))))
                b = __pytra_int((255.0 * (1.0 - t)))
            end
            push!(pixels, r)
            push!(pixels, g)
            push!(pixels, b)
        end
    end
    return pixels
end

function run_julia()
    width = 3840
    height = 2160
    max_iter = 20000
    out_path = "sample/out/03_julia_set.png"
    
    start = perf_counter()
    pixels = render_julia(width, height, max_iter, (-0.8), 0.156)
    png.write_rgb_png(out_path, width, height, pixels)
    elapsed = (perf_counter() - start)
    
    __pytra_print("output:", out_path)
    __pytra_print("size:", width, "x", height)
    __pytra_print("max_iter:", max_iter)
    __pytra_print("elapsed_sec:", elapsed)
end


run_julia();
