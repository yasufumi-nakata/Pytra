// Native implementation of pytra.std.os_path for Zig.
// source: src/pytra/std/os_path.py

const std = @import("std");

pub fn join(a: []const u8, b: []const u8) []const u8 {
    const alloc = std.heap.page_allocator;
    return std.fs.path.join(alloc, &[_][]const u8{ a, b }) catch "";
}

pub fn dirname(p: []const u8) []const u8 {
    return std.fs.path.dirname(p) orelse "";
}

pub fn basename(p: []const u8) []const u8 {
    return std.fs.path.basename(p);
}

pub fn splitext(p: []const u8) struct { _0: []const u8, _1: []const u8 } {
    const base = basename(p);
    const dot = std.mem.lastIndexOfScalar(u8, base, '.') orelse return .{ ._0 = p, ._1 = "" };
    const prefix_len = p.len - base.len + dot;
    return .{ ._0 = p[0..prefix_len], ._1 = base[dot..] };
}

pub fn abspath(p: []const u8) []const u8 {
    return p;
}

pub fn exists(p: []const u8) bool {
    _ = std.fs.cwd().statFile(p) catch return false;
    return true;
}
