<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.math for PHP.
 *
 * Provides __native_<func> implementations and __native_<var> constants
 * that the emitter-generated std/math.php delegates to via @extern convention.
 *
 * source: src/pytra/std/math.py
 */

$__native_pi = M_PI;
$__native_e = M_E;

if (!function_exists('__native_sqrt')) {
    function __native_sqrt($x) { return sqrt((float)$x); }
}
if (!function_exists('__native_sin')) {
    function __native_sin($x) { return sin((float)$x); }
}
if (!function_exists('__native_cos')) {
    function __native_cos($x) { return cos((float)$x); }
}
if (!function_exists('__native_tan')) {
    function __native_tan($x) { return tan((float)$x); }
}
if (!function_exists('__native_exp')) {
    function __native_exp($x) { return exp((float)$x); }
}
if (!function_exists('__native_log')) {
    function __native_log($x) { return log((float)$x); }
}
if (!function_exists('__native_log10')) {
    function __native_log10($x) { return log10((float)$x); }
}
if (!function_exists('__native_fabs')) {
    function __native_fabs($x) { return abs((float)$x); }
}
if (!function_exists('__native_floor')) {
    function __native_floor($x) { return (float)floor((float)$x); }
}
if (!function_exists('__native_ceil')) {
    function __native_ceil($x) { return (float)ceil((float)$x); }
}
if (!function_exists('__native_pow')) {
    function __native_pow($a, $b) { return pow((float)$a, (float)$b); }
}
if (!function_exists('__native_atan2')) {
    function __native_atan2($y, $x) { return atan2((float)$y, (float)$x); }
}
if (!function_exists('__native_acos')) {
    function __native_acos($x) { return acos((float)$x); }
}
if (!function_exists('__native_asin')) {
    function __native_asin($x) { return asin((float)$x); }
}
