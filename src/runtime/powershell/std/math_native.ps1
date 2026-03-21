# math_native.ps1 — native seam for pytra.std.math
# Generated std/math/east.ps1 delegates extern bindings through this file.

$script:pi = [Math]::PI
$script:e  = [Math]::E

function sqrt  { param($x) return [Math]::Sqrt($x) }
function sin_  { param($x) return [Math]::Sin($x) }
function cos_  { param($x) return [Math]::Cos($x) }
function tan_  { param($x) return [Math]::Tan($x) }
function asin_ { param($x) return [Math]::Asin($x) }
function acos_ { param($x) return [Math]::Acos($x) }
function atan_ { param($x) return [Math]::Atan($x) }
function atan2_ { param($x, $y) return [Math]::Atan2($x, $y) }
function exp_  { param($x) return [Math]::Exp($x) }
function log_  { param($x) return [Math]::Log($x) }
function log10_ { param($x) return [Math]::Log10($x) }
function log2_  { param($x) return [Math]::Log($x, 2) }
function fabs  { param($x) return [Math]::Abs($x) }
function floor_ { param($x) return [int][Math]::Floor($x) }
function ceil_  { param($x) return [int][Math]::Ceiling($x) }
function pow_  { param($x, $y) return [Math]::Pow($x, $y) }
function round_ { param($x, $n = 0) return [Math]::Round($x, $n) }
function trunc_ { param($x) return [int][Math]::Truncate($x) }
