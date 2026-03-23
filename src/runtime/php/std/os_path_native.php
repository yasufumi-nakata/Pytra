<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.os_path for PHP.
 *
 * source: src/pytra/std/os_path.py
 */

if (!function_exists('__native_join')) {
    function __native_join($a, $b): string {
        $sa = (string)$a;
        $sb = (string)$b;
        if ($sa === '' || $sb === '' || $sb[0] === '/') {
            return $sb !== '' ? $sb : $sa;
        }
        if (substr($sa, -1) === '/') {
            return $sa . $sb;
        }
        return $sa . '/' . $sb;
    }
}

if (!function_exists('__native_dirname')) {
    function __native_dirname($p): string {
        return dirname((string)$p);
    }
}

if (!function_exists('__native_basename')) {
    function __native_basename($p): string {
        return basename((string)$p);
    }
}

if (!function_exists('__native_splitext')) {
    function __native_splitext($p): array {
        $path = (string)$p;
        $ext = '';
        $dot = strrpos(basename($path), '.');
        if ($dot !== false && $dot > 0) {
            $ext = substr(basename($path), $dot);
            $root = substr($path, 0, strlen($path) - strlen($ext));
        } else {
            $root = $path;
        }
        return [$root, $ext];
    }
}

if (!function_exists('__native_abspath')) {
    function __native_abspath($p): string {
        $path = (string)$p;
        $resolved = realpath($path);
        if ($resolved === false) {
            // If file doesn't exist, resolve relative to cwd
            if ($path !== '' && $path[0] !== '/') {
                return getcwd() . '/' . $path;
            }
            return $path;
        }
        return $resolved;
    }
}

if (!function_exists('__native_exists')) {
    function __native_exists($p): bool {
        return file_exists((string)$p);
    }
}
