#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# import: pytra.std.time

function run_integer_grid_checksum {
    param($width, $height, $seed)
    $mod_main = 2147483647
    $mod_out = 1000000007
    $acc = ($seed % $mod_out)
    for ($y = 0; ($y -lt $height); $y++) {
        $row_sum = 0
        for ($x = 0; ($x -lt $width); $x++) {
            $v = (((($x * 37) + ($y * 73)) + $seed) % $mod_main)
            $v = ((($v * 48271) + 1) % $mod_main)
            $row_sum += ($v % 256)
        }
        $acc = (($acc + ($row_sum * ($y + 1))) % $mod_out)
    }
    return $acc
}

function run_integer_benchmark {
    param()
    $width = 7600
    $height = 5000
    $start = (perf_counter)
    $checksum = (run_integer_grid_checksum $width $height 123456789)
    $elapsed = ((perf_counter) - $start)
    __pytra_print "pixels:" ($width * $height)
    __pytra_print "checksum:" $checksum
    __pytra_print "elapsed_sec:" $elapsed
}

(run_integer_benchmark)
