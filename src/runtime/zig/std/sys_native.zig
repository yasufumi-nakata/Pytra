const std = @import("std");
const pytra = @import("../built_in/py_runtime.zig");

const EmptyVTable = struct {};
var argv_store = std.ArrayList([]const u8).init(std.heap.page_allocator);
var path_store = std.ArrayList([]const u8).init(std.heap.page_allocator);
var argv_rc: usize = 1;
var path_rc: usize = 1;

pub const argv: pytra.Obj = .{
    .data = @ptrCast(&argv_store),
    .vtable = @ptrCast(&EmptyVTable),
    .rc = &argv_rc,
    .drop_fn = null,
};
pub const path: pytra.Obj = .{
    .data = @ptrCast(&path_store),
    .vtable = @ptrCast(&EmptyVTable),
    .rc = &path_rc,
    .drop_fn = null,
};
pub const stderr: []const u8 = "stderr";
pub const stdout: []const u8 = "stdout";

pub fn exit(code: i64) void {
    std.process.exit(@intCast(code));
}

pub fn set_argv(values: pytra.Obj) void {
    const src = values.as(std.ArrayList([]const u8));
    argv_store.clearRetainingCapacity();
    argv_store.appendSlice(src.items) catch {};
}

pub fn set_path(values: pytra.Obj) void {
    const src = values.as(std.ArrayList([]const u8));
    path_store.clearRetainingCapacity();
    path_store.appendSlice(src.items) catch {};
}

pub fn write_stderr(text: []const u8) void {
    std.io.getStdErr().writer().writeAll(text) catch {};
}

pub fn write_stdout(text: []const u8) void {
    std.io.getStdOut().writer().writeAll(text) catch {};
}
