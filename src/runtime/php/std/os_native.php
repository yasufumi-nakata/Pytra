<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.os for PHP.
 *
 * source: src/pytra/std/os.py
 */

if (!function_exists('__native_getcwd')) {
    function __native_getcwd(): string {
        return (string)getcwd();
    }
}

if (!function_exists('__native_mkdir')) {
    function __native_mkdir($p): void {
        $path = (string)$p;
        if (!is_dir($path)) {
            mkdir($path);
        }
    }
}

if (!function_exists('__native_makedirs')) {
    function __native_makedirs($p, $exist_ok = false): void {
        $path = (string)$p;
        if ($exist_ok && is_dir($path)) {
            return;
        }
        mkdir($path, 0777, true);
    }
}
