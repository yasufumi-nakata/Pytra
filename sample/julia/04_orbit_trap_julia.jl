include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "png.jl"))
png = (_adler32=_adler32, _chunk=_chunk, _crc32=_crc32, _png_append_list=_png_append_list, _png_u16le=_png_u16le, _png_u32be=_png_u32be, _zlib_deflate_store=_zlib_deflate_store, write_rgb_png=write_rgb_png)

# 04: Sample that renders an orbit-trap Julia set and writes a PNG image.

function render_orbit_trap_julia(width, height, max_iter, cx, cy)
    pixels = UInt8[]
    
    for y in 0:height - 1
        zy0 = ((-1.3) + (2.6 * (y / (height - 1))))
        for x in 0:width - 1
            zx = ((-1.9) + (3.8 * (x / (width - 1))))
            zy = zy0
            
            trap = 1000000000.0
            i = 0
            while (i < max_iter)
                ax = zx
                if (ax < 0.0)
                    ax = (-ax)
                end
                ay = zy
                if (ay < 0.0)
                    ay = (-ay)
                end
                dxy = (zx - zy)
                if (dxy < 0.0)
                    dxy = (-dxy)
                end
                if (ax < trap)
                    trap = ax
                end
                if (ay < trap)
                    trap = ay
                end
                if (dxy < trap)
                    trap = dxy
                end
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
                trap_scaled = (trap * 3.2)
                if (trap_scaled > 1.0)
                    trap_scaled = 1.0
                end
                if (trap_scaled < 0.0)
                    trap_scaled = 0.0
                end
                t = (i / max_iter)
                tone = __pytra_int((255.0 * (1.0 - trap_scaled)))
                r = __pytra_int((tone * (0.35 + (0.65 * t))))
                g = __pytra_int((tone * (0.15 + (0.85 * (1.0 - t)))))
                b = __pytra_int((255.0 * (0.25 + (0.75 * t))))
                if (r > 255)
                    r = 255
                end
                if (g > 255)
                    g = 255
                end
                if (b > 255)
                    b = 255
                end
            end
            push!(pixels, r)
            push!(pixels, g)
            push!(pixels, b)
        end
    end
    return pixels
end

function run_04_orbit_trap_julia()
    width = 1920
    height = 1080
    max_iter = 1400
    out_path = "sample/out/04_orbit_trap_julia.png"
    
    start = perf_counter()
    pixels = render_orbit_trap_julia(width, height, max_iter, (-0.7269), 0.1889)
    png.write_rgb_png(out_path, width, height, pixels)
    elapsed = (perf_counter() - start)
    
    __pytra_print("output:", out_path)
    __pytra_print("size:", width, "x", height)
    __pytra_print("max_iter:", max_iter)
    __pytra_print("elapsed_sec:", elapsed)
end


run_04_orbit_trap_julia();
