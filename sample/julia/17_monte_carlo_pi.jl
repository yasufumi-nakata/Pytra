include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "pathlib.jl"))
include(joinpath(@__DIR__, "std", "time.jl"))

# 17: Sample that scans a large grid using integer arithmetic only and computes a checksum.
# It avoids floating-point error effects, making cross-language comparisons easier.

function run_integer_grid_checksum(width, height, seed)
    mod_main = 2147483647
    mod_out = 1000000007
    acc = (seed % mod_out)
    
    for y in 0:height - 1
        row_sum = 0
        for x in 0:width - 1
            v = ((((x * 37) + (y * 73)) + seed) % mod_main)
            v = (((v * 48271) + 1) % mod_main)
            row_sum = row_sum + (v % 256)
        end
        acc = ((acc + (row_sum * (y + 1))) % mod_out)
    end
    return acc
end

function run_integer_benchmark()
    # Previous baseline: 2400 x 1600 (= 3,840,000 cells).
    # 7600 x 5000 (= 38,000,000 cells) is ~9.9x larger to make this case
    # meaningful in runtime benchmarks.
    width = 7600
    height = 5000
    out_path = "sample/out/17_monte_carlo_pi.txt"
    
    start = perf_counter()
    checksum = run_integer_grid_checksum(width, height, 123456789)
    elapsed = (perf_counter() - start)
    
    result = (((("pixels:" * string((width * height))) * "\nchecksum:") * string(checksum)) * "\n")
    p = Path(out_path)
    write_text(p, result, "utf-8")
    
    __pytra_print("pixels:", (width * height))
    __pytra_print("checksum:", checksum)
    __pytra_print("elapsed_sec:", elapsed)
end


run_integer_benchmark();
