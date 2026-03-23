// Native implementation of pytra.std.glob for Zig.
// source: src/pytra/std/glob.py

const std = @import("std");

pub fn glob(pattern: []const u8) [][]const u8 {
    _ = pattern;
    // Stub: Zig has no built-in glob; return empty for now
    return &[_][]const u8{};
}
