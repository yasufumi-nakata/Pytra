# math_native.ps1 — native seam for pytra.std.math
# Generated std/math/east.ps1 delegates extern bindings through this file.

$script:pi = [Math]::PI
$script:e  = [Math]::E

function sqrt   { param($x) return [Math]::Sqrt($x) }
function sin    { param($x) return [Math]::Sin($x) }
function cos    { param($x) return [Math]::Cos($x) }
function tan    { param($x) return [Math]::Tan($x) }
function asin   { param($x) return [Math]::Asin($x) }
function acos   { param($x) return [Math]::Acos($x) }
function atan   { param($x) return [Math]::Atan($x) }
function atan2  { param($x, $y) return [Math]::Atan2($x, $y) }
function exp    { param($x) return [Math]::Exp($x) }
function log    { param($x) return [Math]::Log($x) }
function log10  { param($x) return [Math]::Log10($x) }
function log2   { param($x) return [Math]::Log($x, 2) }
function fabs   { param($x) return [Math]::Abs($x) }
function floor  { param($x) return [int][Math]::Floor($x) }
function ceil   { param($x) return [int][Math]::Ceiling($x) }
function pow    { param($x, $y) return [Math]::Pow($x, $y) }
function round  { param($x, $n = 0) return [Math]::Round($x, $n) }
function trunc  { param($x) return [int][Math]::Truncate($x) }
