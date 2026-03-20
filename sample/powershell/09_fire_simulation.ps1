#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

import { perf_counter } from "./runtime/js/generated/std/time.js"
import { save_gif } from "./runtime/js/generated/utils/gif.js"

# 09: Sample that outputs a simple fire effect as a GIF.

function fire_palette {
    param()
    $p = @()
    for ($i = 0; $i  -$lt  256; $i += 1) {
        $r = 0
        $g = 0
        $b = 0
        if ($i  -$lt  85) {
            r = i * 3
            g = 0
            b = 0
        } else {
            if ($i  -$lt  170) {
                r = 255
                g = (i - 85) * 3
                b = 0
            } else {
                r = 255
                g = 255
                b = (i - 170) * 3
            }
        }
        p.push(r)
        p.push(g)
        p.push(b)
    }
    return ($Array.isArray((p)) ? (p).slice() : $Array.from((p)))
}

function run_09_fire_simulation {
    param()
    $w = 380
    $h = 260
    $steps = 420
    $out_path = "sample/out/09_fire_simulation.gif"

    $start = $perf_counter
    $heat = (() = -$gt  { $let $__out = []; for ($const $_ of (() = -$gt  { $const $__out = []; $const $__start = 0; $const $__stop = $h; $const $__step = 1; if ($__step -$eq 0) { return $__out; } if ($__step  -$gt  0) { for ($let $__i = $__start; $__i  -$lt  $__stop; $__i += __step) { $__out.push(__i); } } else { for ($let $__i = $__start; $__i  -$gt  $__stop; $__i += __step) { $__out.push(__i); } } return $__out; })()) { $__out.push((() = -$gt  { $const $__base = ([0]); $const $__n = [Math]::$Max 0 Math.trunc(Number(w)); $let $__out = []; for ($let $__i = 0; $__i  -$lt  $__n; $__i += 1) { for ($const $__v $of __base) { $__out.push(__v); } } return $__out; })()); } return $__out; })()
    $frames = @()

    for ($t = 0; $t  -$lt  $steps; $t += 1) {
        for ($x = 0; $x  -$lt  $w; $x += 1) {
            $val = 170 + ($x * 13 + $t * 17) % 86
            heat[(((h - 1)  -lt  0) ? ((heat).Length + (h - 1)) : (h - 1))][(((x)  -lt  0) ? ((heat[(((h - 1)  -lt  0) ? ((heat).Length + (h - 1)) : (h - 1))]).Length + (x)) : (x))] = val
        }
        for ($y = 1; $y  -$lt  $h; $y += 1) {
            for ($x = 0; $x  -$lt  $w; $x += 1) {
                $a = $heat[(((y)  -$lt  0) ? ((heat).Length + (y)) : (y))][(((x)  -$lt  0) ? (($heat[(((y)  -$lt  0) ? ((heat).Length + (y)) : (y))]).Length + (x)) : (x))]
                $b = $heat[(((y)  -$lt  0) ? ((heat).Length + (y)) : (y))][(((($x - 1 + w) % w)  -$lt  0) ? (($heat[(((y)  -$lt  0) ? ((heat).Length + (y)) : (y))]).Length + (($x - 1 + w) % w)) : (($x - 1 + w) % w))]
                $c = $heat[(((y)  -$lt  0) ? ((heat).Length + (y)) : (y))][(((($x + 1) % w)  -$lt  0) ? (($heat[(((y)  -$lt  0) ? ((heat).Length + (y)) : (y))]).Length + (($x + 1) % w)) : (($x + 1) % w))]
                $d = $heat[(((($y + 1) % h)  -$lt  0) ? ((heat).Length + (($y + 1) % h)) : (($y + 1) % h))][(((x)  -$lt  0) ? (($heat[(((($y + 1) % h)  -$lt  0) ? ((heat).Length + (($y + 1) % h)) : (($y + 1) % h))]).Length + (x)) : (x))]
                $v = [Math]::Floor ($a + $b + $c + $d / 4)
                $cool = 1 + ($x + $y + t) % 3
                $nv = $v - $cool
                heat[(((y - 1)  -lt  0) ? ((heat).Length + (y - 1)) : (y - 1))][(((x)  -lt  0) ? ((heat[(((y - 1)  -lt  0) ? ((heat).Length + (y - 1)) : (y - 1))]).Length + (x)) : (x))] = (nv  -gt  0 ? nv : 0)
            }
        }
        $frame = ($typeof $w * $h -$eq "number" ? $Array [Math]::Max(0, Math.trunc(Number(($w * h)))).fill(0) : ($Array.isArray(($w * h)) ? ($w * h).slice() : $Array.from(($w * h))))
        for ($yy = 0; $yy  -$lt  $h; $yy += 1) {
            $row_base = $yy * $w
            for ($xx = 0; $xx  -$lt  $w; $xx += 1) {
                frame[(((row_base + xx)  -lt  0) ? ((frame).Length + (row_base + xx)) : (row_base + xx))] = heat[(((yy)  -lt  0) ? ((heat).Length + (yy)) : (yy))][(((xx)  -lt  0) ? ((heat[(((yy)  -lt  0) ? ((heat).Length + (yy)) : (yy))]).Length + (xx)) : (xx))]
            }
        }
        frames.push((Array.isArray((frame)) ? (frame).slice() : Array.from((frame))))
    }
    save_gif out_path w h frames fire_palette(, 4, 0)
    $elapsed = $perf_counter - $start
    __pytra_print "output:" out_path
    __pytra_print "frames:" steps
    __pytra_print "elapsed_sec:" elapsed
}

run_09_fire_simulation

if (Get-Command -Name main -ErrorAction SilentlyContinue) {
    main
}
