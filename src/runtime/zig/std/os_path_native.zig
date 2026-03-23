// Native implementation of pytra.std.os_path for Zig.
// source: src/pytra/std/os_path.py

const std = @import("std");

pub fn join(a: []const u8, b: []const u8) []const u8 {
    _ = a;
    _ = b;
    return "";
}

pub fn dirname(p: []const u8) []const u8 {
    return std.fs.path.dirname(p) orelse "";
}

pub fn basename(p: []const u8) []const u8 {
    return std.fs.path.basename(p);
}

pub fn exists(p: []const u8) bool {
    _ = std.fs.cwd().statFile(p) catch return false;
    return true;
}
