#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# import: pytra.std

# import: pytra.std.time

# import: pytra.utils.gif

function palette {
    param()
    $p = (bytearray)
    for ($i = 0; ($i -lt 256); $i++) {
        $r = [Math]::Min(255, __pytra_int (20 + ($i * 0.9)))
        $g = [Math]::Min(255, __pytra_int (10 + ($i * 0.7)))
        $b = [Math]::Min(255, (30 + $i))
        $p += @($r)
        $p += @($g)
        $p += @($b)
    }
    return (bytes $p)
}

function scene {
    param($x, $y, $light_x, $light_y)
    $x1 = ($x + 0.45)
    $y1 = ($y + 0.2)
    $x2 = ($x - 0.35)
    $y2 = ($y - 0.15)
    $r1 = $math.sqrt((($x1 * $x1) + ($y1 * $y1)))
    $r2 = $math.sqrt((($x2 * $x2) + ($y2 * $y2)))
    $blob = ($math.exp((((-7.0) * $r1) * $r1)) + $math.exp((((-8.0) * $r2) * $r2)))
    $lx = ($x - $light_x)
    $ly = ($y - $light_y)
    $l = $math.sqrt((($lx * $lx) + ($ly * $ly)))
    $lit = (1.0 / (1.0 + ((3.5 * $l) * $l)))
    $v = __pytra_int (((255.0 * $blob) * $lit) * 5.0)
    return [Math]::Min(255, [Math]::Max(0, $v))
}

function run_14_raymarching_light_cycle {
    param()
    $w = 320
    $h = 240
    $frames_n = 84
    $out_path = "sample/out/14_raymarching_light_cycle.gif"
    $start = (perf_counter)
    $frames = @()
    $__hoisted_cast_1 = __pytra_float $frames_n
    $__hoisted_cast_2 = __pytra_float ($h - 1)
    $__hoisted_cast_3 = __pytra_float ($w - 1)
    for ($t = 0; ($t -lt $frames_n); $t++) {
        $frame = (bytearray ($w * $h))
        $a = ((($t / $__hoisted_cast_1) * $math.pi) * 2.0)
        $light_x = (0.75 * $math.cos($a))
        $light_y = (0.55 * $math.sin(($a * 1.2)))
        for ($y = 0; ($y -lt $h); $y++) {
            $row_base = ($y * $w)
            $py = ((($y / $__hoisted_cast_2) * 2.0) - 1.0)
            for ($x = 0; ($x -lt $w); $x++) {
                $px = ((($x / $__hoisted_cast_3) * 2.0) - 1.0)
                $frame[($row_base + $x)] = (scene $px $py $light_x $light_y)
            }
        }
        $frames += @((bytes $frame))
    }
    (save_gif $out_path $w $h $frames (palette))
    $elapsed = ((perf_counter) - $start)
    __pytra_print "output:" $out_path
    __pytra_print "frames:" $frames_n
    __pytra_print "elapsed_sec:" $elapsed
}

(run_14_raymarching_light_cycle)
