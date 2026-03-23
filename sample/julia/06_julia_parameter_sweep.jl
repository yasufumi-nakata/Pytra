include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "math.jl"))
math = (ceil=ceil, cos=cos, e=e, exp=exp, fabs=fabs, floor=floor, log=log, log10=log10, pi=pi, pow=pow, sin=sin, sqrt=sqrt, tan=tan)
include(joinpath(@__DIR__, "std", "time.jl"))
include(joinpath(@__DIR__, "utils", "gif.jl"))

# 06: Sample that sweeps Julia-set parameters and outputs a GIF.

function julia_palette()
    # Keep index 0 black for points inside the set; build a high-saturation gradient for the rest.
    palette = __pytra_bytearray((256 * 3))
    palette[1] = 0
    palette[2] = 0
    palette[3] = 0
    for i in 1:256 - 1
        t = ((i - 1) / 254.0)
        r = __pytra_int((255.0 * ((((9.0 * (1.0 - t)) * t) * t) * t)))
        g = __pytra_int((255.0 * ((((15.0 * (1.0 - t)) * (1.0 - t)) * t) * t)))
        b = __pytra_int((255.0 * ((((8.5 * (1.0 - t)) * (1.0 - t)) * (1.0 - t)) * t)))
        palette[__pytra_idx(((i * 3) + 0), length(palette))] = r
        palette[__pytra_idx(((i * 3) + 1), length(palette))] = g
        palette[__pytra_idx(((i * 3) + 2), length(palette))] = b
    end
    return __pytra_bytes(palette)
end

function render_frame(width, height, cr, ci, max_iter, phase)
    frame = __pytra_bytearray((width * height))
    for y in 0:height - 1
        row_base = (y * width)
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
                zy = (((2.0 * zx) * zy) + ci)
                zx = ((zx2 - zy2) + cr)
                i = i + 1
            end
            if (i >= max_iter)
                frame[__pytra_idx((row_base + x), length(frame))] = 0
            else
                # Add a small frame phase so colors flow smoothly.
                color_index = (1 + ((((i * 224) ÷ max_iter) + phase) % 255))
                frame[__pytra_idx((row_base + x), length(frame))] = color_index
            end
        end
    end
    return __pytra_bytes(frame)
end

function run_06_julia_parameter_sweep()
    width = 320
    height = 240
    frames_n = 72
    max_iter = 180
    out_path = "sample/out/06_julia_parameter_sweep.gif"
    
    start = perf_counter()
    frames = Any[]
    # Orbit an ellipse around a known visually good region to reduce flat blown highlights.
    center_cr = (-0.745)
    center_ci = 0.186
    radius_cr = 0.12
    radius_ci = 0.1
    # Add start and phase offsets so GitHub thumbnails do not appear too dark.
    # Tune it to start in a red-leaning color range.
    start_offset = 20
    phase_offset = 180
    for i in 0:frames_n - 1
        t = (((i + start_offset) % frames_n) / frames_n)
        angle = ((2.0 * math.pi) * t)
        cr = (center_cr + (radius_cr * math.cos(angle)))
        ci = (center_ci + (radius_ci * math.sin(angle)))
        phase = ((phase_offset + (i * 5)) % 255)
        push!(frames, render_frame(width, height, cr, ci, max_iter, phase))
    end
    save_gif(out_path, width, height, frames, julia_palette(), 8, 0)
    elapsed = (perf_counter() - start)
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
end


run_06_julia_parameter_sweep();
