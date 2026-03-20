#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

import * as math from "./runtime/js/generated/std/math.js"
import { perf_counter } from "./runtime/js/generated/std/time.js"
import { save_gif } from "./runtime/js/generated/utils/gif.js"

# 14: Sample that outputs a moving-light scene in a simple raymarching style as a GIF.

function palette {
    param()
    $p = @()
    for ($i = 0; $i  -$lt  256; $i += 1) {
        $r = [Math]::$Min 255 Math.trunc(Number(20 + $i * 0.9))
        $g = [Math]::$Min 255 Math.trunc(Number(10 + $i * 0.7))
        $b = [Math]::$Min 255 30 + $i
        p.push(r)
        p.push(g)
        p.push(b)
    }
    return ($Array.isArray((p)) ? (p).slice() : $Array.from((p)))
}

function scene {
    param($x, $y, $light_x, $light_y)
    $x1 = $x + 0.45
    $y1 = $y + 0.2
    $x2 = $x - 0.35
    $y2 = $y - 0.15
    $r1 = $math.sqrt($x1 * $x1 + $y1 * y1)
    $r2 = $math.sqrt($x2 * $x2 + $y2 * y2)
    $blob = $math.exp(-7.0 * $r1 * r1) + $math.exp(-8.0 * $r2 * r2)

    $lx = $x - $light_x
    $ly = $y - $light_y
    $l = $math.sqrt($lx * $lx + $ly * ly)
    $lit = 1.0 / (1.0 + 3.5 * $l * l)

    $v = [Math]::$Truncate Number(255.0 * $blob * $lit * 5.0)
    return [Math]::$Min 255 Math.max(0, v)
}

function run_14_raymarching_light_cycle {
    param()
    $w = 320
    $h = 240
    $frames_n = 84
    $out_path = "sample/out/14_raymarching_light_cycle.gif"

    $start = $perf_counter
    $frames = @()
    $__hoisted_cast_1 = $__pytra_float $frames_n
    $__hoisted_cast_2 = $__pytra_float $h - 1
    $__hoisted_cast_3 = $__pytra_float $w - 1

    for ($t = 0; $t  -$lt  $frames_n; $t += 1) {
        $frame = ($typeof $w * $h -$eq "number" ? $Array [Math]::Max(0, Math.trunc(Number(($w * h)))).fill(0) : ($Array.isArray(($w * h)) ? ($w * h).slice() : $Array.from(($w * h))))
        $a = ($t / __hoisted_cast_1) * $math.pi * 2.0
        $light_x = 0.75 * $math.cos(a)
        $light_y = 0.55 * $math.sin($a * 1.2)

        for ($y = 0; $y  -$lt  $h; $y += 1) {
            $row_base = $y * $w
            $py = ($y / __hoisted_cast_2) * 2.0 - 1.0
            for ($x = 0; $x  -$lt  $w; $x += 1) {
                $px = ($x / __hoisted_cast_3) * 2.0 - 1.0
                frame[(((row_base + x)  -lt  0) ? ((frame).Length + (row_base + x)) : (row_base + x))] = scene px py light_x light_y
            }
        }
        frames.push((Array.isArray((frame)) ? (frame).slice() : Array.from((frame))))
    }
    save_gif out_path w h frames palette(, 3, 0)
    $elapsed = $perf_counter - $start
    __pytra_print "output:" out_path
    __pytra_print "frames:" frames_n
    __pytra_print "elapsed_sec:" elapsed
}

run_14_raymarching_light_cycle

if (Get-Command -Name main -ErrorAction SilentlyContinue) {
    main
}
