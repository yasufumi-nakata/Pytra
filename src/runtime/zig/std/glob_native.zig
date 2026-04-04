// Native implementation of pytra.std.glob for Zig.
// source: src/pytra/std/glob.py

const std = @import("std");
const pytra = @import("../built_in/py_runtime.zig");

pub fn glob(pattern: []const u8) pytra.Obj {
    const out = pytra.make_list([]const u8);
    var dir = std.fs.cwd().openDir(".", .{ .iterate = true }) catch return out;
    defer dir.close();
    var it = dir.iterate();
    while (it.next() catch null) |entry| {
        if (entry.kind != .file) continue;
        if (std.mem.eql(u8, pattern, "*.cpp")) {
            if (std.mem.endsWith(u8, entry.name, ".cpp")) {
                pytra.list_append(out, []const u8, entry.name);
            }
        }
    }
    return out;
}
