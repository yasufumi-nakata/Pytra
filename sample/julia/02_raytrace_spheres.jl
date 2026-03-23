include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "math.jl"))
math = (ceil=ceil, cos=cos, e=e, exp=exp, fabs=fabs, floor=floor, log=log, log10=log10, pi=pi, pow=pow, sin=sin, sqrt=sqrt, tan=tan)
include(joinpath(@__DIR__, "utils", "png.jl"))
png = (_adler32=_adler32, _chunk=_chunk, _crc32=_crc32, _png_append_list=_png_append_list, _png_u16le=_png_u16le, _png_u32be=_png_u32be, _zlib_deflate_store=_zlib_deflate_store, write_rgb_png=write_rgb_png)
include(joinpath(@__DIR__, "std", "time.jl"))

# 02: Sample that runs a mini sphere-only ray tracer and outputs a PNG image.
# Dependencies are kept minimal (time only) for transpilation compatibility.

function clamp01(v)
    if (v < 0.0)
        return 0.0
    end
    if (v > 1.0)
        return 1.0
    end
    return v
end

function hit_sphere(ox, oy, oz, dx, dy, dz, cx, cy, cz, r)
    lx = (ox - cx)
    ly = (oy - cy)
    lz = (oz - cz)
    
    a = (((dx * dx) + (dy * dy)) + (dz * dz))
    b = (2.0 * (((lx * dx) + (ly * dy)) + (lz * dz)))
    c = ((((lx * lx) + (ly * ly)) + (lz * lz)) - (r * r))
    
    d = ((b * b) - ((4.0 * a) * c))
    if (d < 0.0)
        return (-1.0)
    end
    sd = math.sqrt(d)
    t0 = (((-b) - sd) / (2.0 * a))
    t1 = (((-b) + sd) / (2.0 * a))
    
    if (t0 > 0.001)
        return t0
    end
    if (t1 > 0.001)
        return t1
    end
    return (-1.0)
end

function render(width, height, aa)
    pixels = UInt8[]
    
    # Camera origin
    ox = 0.0
    oy = 0.0
    oz = (-3.0)
    
    # Light direction (normalized)
    lx = (-0.4)
    ly = 0.8
    lz = (-0.45)
    
    for y in 0:height - 1
        for x in 0:width - 1
            ar = 0
            ag = 0
            ab = 0
            
            for ay in 0:aa - 1
                for ax in 0:aa - 1
                    fy = ((y + ((ay + 0.5) / aa)) / (height - 1))
                    fx = ((x + ((ax + 0.5) / aa)) / (width - 1))
                    sy = (1.0 - (2.0 * fy))
                    sx = (((2.0 * fx) - 1.0) * (width / height))
                    
                    dx = sx
                    dy = sy
                    dz = 1.0
                    inv_len = (1.0 / math.sqrt((((dx * dx) + (dy * dy)) + (dz * dz))))
                    dx = dx * inv_len
                    dy = dy * inv_len
                    dz = dz * inv_len
                    
                    t_min = 1e+30
                    hit_id = (-1)
                    
                    t = hit_sphere(ox, oy, oz, dx, dy, dz, (-0.8), (-0.2), 2.2, 0.8)
                    if ((t > 0.0) && (t < t_min))
                        t_min = t
                        hit_id = 0
                    end
                    t = hit_sphere(ox, oy, oz, dx, dy, dz, 0.9, 0.1, 2.9, 0.95)
                    if ((t > 0.0) && (t < t_min))
                        t_min = t
                        hit_id = 1
                    end
                    t = hit_sphere(ox, oy, oz, dx, dy, dz, 0.0, (-1001.0), 3.0, 1000.0)
                    if ((t > 0.0) && (t < t_min))
                        t_min = t
                        hit_id = 2
                    end
                    r = 0
                    g = 0
                    b = 0
                    
                    if (hit_id >= 0)
                        px = (ox + (dx * t_min))
                        py = (oy + (dy * t_min))
                        pz = (oz + (dz * t_min))
                        
                        nx = 0.0
                        ny = 0.0
                        nz = 0.0
                        
                        if (hit_id == 0)
                            nx = ((px + 0.8) / 0.8)
                            ny = ((py + 0.2) / 0.8)
                            nz = ((pz - 2.2) / 0.8)
                        elseif (hit_id == 1)
                            nx = ((px - 0.9) / 0.95)
                            ny = ((py - 0.1) / 0.95)
                            nz = ((pz - 2.9) / 0.95)
                        else
                            nx = 0.0
                            ny = 1.0
                            nz = 0.0
                        end
                        diff = (((nx * (-lx)) + (ny * (-ly))) + (nz * (-lz)))
                        diff = clamp01(diff)
                        
                        base_r = 0.0
                        base_g = 0.0
                        base_b = 0.0
                        
                        if (hit_id == 0)
                            base_r = 0.95
                            base_g = 0.35
                            base_b = 0.25
                        elseif (hit_id == 1)
                            base_r = 0.25
                            base_g = 0.55
                            base_b = 0.95
                        else
                            checker = (__pytra_int(((px + 50.0) * 0.8)) + __pytra_int(((pz + 50.0) * 0.8)))
                            if ((checker % 2) == 0)
                                base_r = 0.85
                                base_g = 0.85
                                base_b = 0.85
                            else
                                base_r = 0.2
                                base_g = 0.2
                                base_b = 0.2
                            end
                        end
                        shade = (0.12 + (0.88 * diff))
                        r = __pytra_int((255.0 * clamp01((base_r * shade))))
                        g = __pytra_int((255.0 * clamp01((base_g * shade))))
                        b = __pytra_int((255.0 * clamp01((base_b * shade))))
                    else
                        tsky = (0.5 * (dy + 1.0))
                        r = __pytra_int((255.0 * (0.65 + (0.2 * tsky))))
                        g = __pytra_int((255.0 * (0.75 + (0.18 * tsky))))
                        b = __pytra_int((255.0 * (0.9 + (0.08 * tsky))))
                    end
                    ar = ar + r
                    ag = ag + g
                    ab = ab + b
                end
            end
            samples = (aa * aa)
            push!(pixels, (ar ÷ samples))
            push!(pixels, (ag ÷ samples))
            push!(pixels, (ab ÷ samples))
        end
    end
    return pixels
end

function run_raytrace()
    width = 1600
    height = 900
    aa = 2
    out_path = "sample/out/02_raytrace_spheres.png"
    
    start = perf_counter()
    pixels = render(width, height, aa)
    png.write_rgb_png(out_path, width, height, pixels)
    elapsed = (perf_counter() - start)
    
    __pytra_print("output:", out_path)
    __pytra_print("size:", width, "x", height)
    __pytra_print("elapsed_sec:", elapsed)
end


run_raytrace();
