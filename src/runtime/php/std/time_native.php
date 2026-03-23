<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.time for PHP.
 *
 * Provides __native_<func> implementations that the emitter-generated
 * std/time.php delegates to via @extern convention.
 *
 * source: src/pytra/std/time.py
 */

if (!function_exists('__native_perf_counter')) {
    function __native_perf_counter(): float {
        return microtime(true);
    }
}
