<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.glob for PHP.
 *
 * source: src/pytra/std/glob.py
 */

if (!function_exists('__native_glob')) {
    function __native_glob($pattern) {
        $result = glob((string)$pattern);
        if ($result === false) {
            return [];
        }
        // Normalize paths to use forward slashes (match Python behavior)
        $out = [];
        foreach ($result as $p) {
            $out[] = str_replace('\\', '/', $p);
        }
        return $out;
    }
}
