// Native implementation of pytra.std.os for Zig.
// source: src/pytra/std/os.py

const std = @import("std");
pub const path = @import("os_path_native.zig");

pub fn getcwd() []const u8 {
    // Stub: return "." for now
    return ".";
}

pub fn mkdir(p: []const u8) void {
    std.fs.cwd().makeDir(p) catch {};
}

pub fn makedirs(p: []const u8, exist_ok: bool) void {
    _ = exist_ok;
    std.fs.cwd().makePath(p) catch {};
}
