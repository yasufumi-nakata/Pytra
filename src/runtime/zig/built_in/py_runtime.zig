// Pytra Zig runtime – minimal built-in helpers.
// This file is loaded by generated Zig programs via @import("py_runtime.zig").

const std = @import("std");

/// Fallback type for unresolved Python types (Any/object/unknown).
pub const PyObject = i64;

/// Print a single value followed by newline, Python-style.
pub fn print(value: anytype) void {
    const writer = std.io.getStdOut().writer();
    printValue(writer, value);
    writer.writeAll("\n") catch {};
}

/// Print two values separated by a space.
pub fn print2(a: anytype, b: anytype) void {
    const writer = std.io.getStdOut().writer();
    printValue(writer, a);
    writer.writeAll(" ") catch {};
    printValue(writer, b);
    writer.writeAll("\n") catch {};
}

/// Print three values separated by spaces.
pub fn print3(a: anytype, b: anytype, c: anytype) void {
    const writer = std.io.getStdOut().writer();
    printValue(writer, a);
    writer.writeAll(" ") catch {};
    printValue(writer, b);
    writer.writeAll(" ") catch {};
    printValue(writer, c);
    writer.writeAll("\n") catch {};
}

fn printValue(writer: anytype, value: anytype) void {
    const T = @TypeOf(value);
    switch (@typeInfo(T)) {
        .int, .comptime_int => {
            writer.print("{d}", .{value}) catch {};
        },
        .float, .comptime_float => {
            printFloat(writer, value);
        },
        .bool => {
            writer.writeAll(if (value) "True" else "False") catch {};
        },
        .pointer => |ptr_info| {
            if (ptr_info.size == .slice and ptr_info.child == u8) {
                writer.writeAll(value) catch {};
            } else if (ptr_info.size == .one) {
                // *const [N:0]u8 (string literal) → coerce to slice
                const child_info = @typeInfo(ptr_info.child);
                if (child_info == .array and child_info.array.child == u8) {
                    writer.writeAll(value) catch {};
                } else {
                    writer.print("{any}", .{value}) catch {};
                }
            } else {
                writer.print("{any}", .{value}) catch {};
            }
        },
        .optional => {
            if (value) |v| {
                printValue(writer, v);
            } else {
                writer.writeAll("None") catch {};
            }
        },
        .null => {
            writer.writeAll("None") catch {};
        },
        .void => {
            writer.writeAll("None") catch {};
        },
        else => {
            writer.print("{any}", .{value}) catch {};
        },
    }
}

fn printFloat(writer: anytype, value: anytype) void {
    // Python-style float printing: no trailing zeros, but at least one decimal
    const v: f64 = @floatCast(value);
    // Check if it's an integer value
    const truncated = @trunc(v);
    if (v == truncated and !std.math.isNan(v) and !std.math.isInf(v)) {
        writer.print("{d}.0", .{@as(i64, @intFromFloat(truncated))}) catch {};
    } else {
        writer.print("{d}", .{v}) catch {};
    }
}

/// Python-style truthiness check.
pub fn truthy(value: anytype) bool {
    const T = @TypeOf(value);
    switch (@typeInfo(T)) {
        .bool => return value,
        .int, .comptime_int => return value != 0,
        .float, .comptime_float => return value != 0.0,
        .optional => return value != null,
        .null => return false,
        .pointer => |ptr_info| {
            if (ptr_info.size == .slice) {
                return value.len > 0;
            }
            return true;
        },
        else => return true,
    }
}

/// Convert a value to string representation.
pub fn to_str(value: anytype) []const u8 {
    const T = @TypeOf(value);
    const alloc = std.heap.page_allocator;
    switch (@typeInfo(T)) {
        .int, .comptime_int => {
            // Format integer to string
            var v: i64 = @intCast(value);
            var neg = false;
            if (v < 0) {
                neg = true;
                v = -v;
            }
            var buf: [20]u8 = undefined;
            var pos: usize = buf.len;
            if (v == 0) {
                pos -= 1;
                buf[pos] = '0';
            } else {
                while (v > 0) {
                    pos -= 1;
                    buf[pos] = @intCast(@as(u8, @intCast(@mod(v, 10))) + '0');
                    v = @divFloor(v, 10);
                }
            }
            if (neg) {
                pos -= 1;
                buf[pos] = '-';
            }
            const len = buf.len - pos;
            const result = alloc.alloc(u8, len) catch return "?";
            @memcpy(result, buf[pos..]);
            return result;
        },
        .float, .comptime_float => {
            // Simple float formatting
            const fv: f64 = @floatCast(value);
            const iv: i64 = @intFromFloat(fv);
            return to_str(iv);
        },
        .bool => {
            return if (value) "True" else "False";
        },
        .pointer => |ptr_info| {
            if (ptr_info.size == .slice and ptr_info.child == u8) {
                return value;
            }
            if (ptr_info.size == .one) {
                const child_info = @typeInfo(ptr_info.child);
                if (child_info == .array and child_info.array.child == u8) {
                    return value;
                }
            }
            return "<object>";
        },
        else => return "<object>",
    }
}

/// Concatenate two strings.
pub fn str_concat(a: []const u8, b: []const u8) []const u8 {
    const alloc = std.heap.page_allocator;
    const buf = alloc.alloc(u8, a.len + b.len) catch return "";
    @memcpy(buf[0..a.len], a);
    @memcpy(buf[a.len..], b);
    return buf;
}

pub fn str_upper(s: []const u8) []const u8 {
    const alloc = std.heap.page_allocator;
    const buf = alloc.alloc(u8, s.len) catch return "";
    for (s, 0..) |ch, i| {
        buf[i] = if (ch >= 'a' and ch <= 'z') ch - 32 else ch;
    }
    return buf;
}

/// Join multiple string slices.
pub fn str_join(parts: anytype) []const u8 {
    const alloc = std.heap.page_allocator;
    var total: usize = 0;
    for (parts) |p| {
        total += p.len;
    }
    const buf = alloc.alloc(u8, total) catch return "";
    var pos: usize = 0;
    for (parts) |p| {
        @memcpy(buf[pos..][0..p.len], p);
        pos += p.len;
    }
    return buf;
}

/// Join string slices with a separator (Python str.join equivalent).
pub fn str_join_sep(sep: []const u8, parts: []const []const u8) []const u8 {
    if (parts.len == 0) return "";
    const alloc = std.heap.page_allocator;
    var total: usize = 0;
    for (parts) |p| {
        total += p.len;
    }
    total += sep.len * (parts.len - 1);
    const buf = alloc.alloc(u8, total) catch return "";
    var pos: usize = 0;
    for (parts, 0..) |p, i| {
        if (i > 0) {
            @memcpy(buf[pos..][0..sep.len], sep);
            pos += sep.len;
        }
        @memcpy(buf[pos..][0..p.len], p);
        pos += p.len;
    }
    return buf;
}

/// Create a new empty StringHashMap.
pub fn make_str_dict(comptime V: type) std.StringHashMap(V) {
    return std.StringHashMap(V).init(std.heap.page_allocator);
}

/// Create a StringHashMap from key/value arrays.
pub fn make_str_dict_from(comptime V: type, keys: []const []const u8, values: []const V) std.StringHashMap(V) {
    var m = std.StringHashMap(V).init(std.heap.page_allocator);
    var i: usize = 0;
    while (i < keys.len and i < values.len) : (i += 1) {
        m.put(keys[i], values[i]) catch {};
    }
    return m;
}

/// isinstance check (stub).
pub fn isinstance_check(obj: anytype, typ: anytype) bool {
    _ = obj;
    _ = typ;
    return false;
}

/// Contains check for `in` operator.
pub fn contains(haystack: anytype, needle: anytype) bool {
    const HT = @TypeOf(haystack);
    // StringHashMap: check if key exists
    if (@typeInfo(HT) == .@"struct" and @hasDecl(HT, "contains")) {
        return haystack.contains(needle);
    }
    if (HT == Obj) {
        const NT = @TypeOf(needle);
        if (NT == i64 or NT == comptime_int) {
            for (list_items(haystack, i64)) |v| {
                if (v == needle) return true;
            }
            return false;
        }
        if (NT == bool) {
            for (list_items(haystack, bool)) |v| {
                if (v == needle) return true;
            }
            return false;
        }
        if (NT == []const u8) {
            for (list_items(haystack, []const u8)) |v| {
                if (std.mem.eql(u8, v, needle)) return true;
            }
            return false;
        }
    }
    return false;
}

/// Reference-counted object wrapper (Pytra Object<T> equivalent).
pub fn Object(comptime T: type) type {
    return struct {
        const Self = @This();
        ptr: *T,
        rc: *usize,

        pub fn init(value: T) Self {
            const alloc = std.heap.page_allocator;
            const p = alloc.create(T) catch @panic("alloc failed");
            p.* = value;
            const rc = alloc.create(usize) catch @panic("alloc failed");
            rc.* = 1;
            return Self{ .ptr = p, .rc = rc };
        }

        pub fn clone(self: Self) Self {
            self.rc.* += 1;
            return Self{ .ptr = self.ptr, .rc = self.rc };
        }

        pub fn release(self: Self) void {
            self.rc.* -= 1;
            if (self.rc.* == 0) {
                const alloc = std.heap.page_allocator;
                alloc.destroy(self.ptr);
                alloc.destroy(self.rc);
            }
        }
    };
}

/// Create a heap-allocated object and return a pointer.
pub fn make_object(comptime T: type, value: T) *T {
    const alloc = std.heap.page_allocator;
    const p = alloc.create(T) catch @panic("alloc failed");
    p.* = value;
    return p;
}

/// Type-erased object with vtable and reference count (spec-object.md §14).
pub const Obj = struct {
    data: *anyopaque,
    vtable: *const anyopaque,
    rc: *usize,
    drop_fn: ?*const fn (*anyopaque) void,

    pub fn retain(self: Obj) Obj {
        self.rc.* += 1;
        return self;
    }

    pub fn release(self: Obj) void {
        if (self.rc.* > 0) {
            self.rc.* -= 1;
            if (self.rc.* == 0) {
                if (self.drop_fn) |drop| {
                    drop(self.data);
                }
            }
        }
    }

    /// Get the vtable cast to a specific VTable type.
    pub fn vt(self: Obj, comptime VT: type) *const VT {
        return @ptrCast(@alignCast(self.vtable));
    }

    /// Get the data pointer cast to a specific type.
    pub fn as(self: Obj, comptime T: type) *T {
        return @ptrCast(@alignCast(self.data));
    }
};

/// Create a type-erased Obj with vtable.
pub fn make_obj(comptime T: type, value: T, vtable: *const anyopaque) Obj {
    return make_obj_drop(T, value, vtable, null);
}

pub fn make_obj_drop(comptime T: type, value: T, vtable: *const anyopaque, drop_fn: ?*const fn (*anyopaque) void) Obj {
    const alloc = std.heap.page_allocator;
    const p = alloc.create(T) catch @panic("alloc failed");
    p.* = value;
    const rc = alloc.create(usize) catch @panic("alloc failed");
    rc.* = 1;
    return Obj{
        .data = @ptrCast(p),
        .vtable = vtable,
        .rc = rc,
        .drop_fn = drop_fn,
    };
}

// ─── List (Obj-managed ArrayList) ───

/// Create an empty list as Obj.
pub fn make_list(comptime T: type) Obj {
    const alloc = std.heap.page_allocator;
    const p = alloc.create(std.ArrayList(T)) catch @panic("alloc failed");
    p.* = std.ArrayList(T).init(alloc);
    const rc = alloc.create(usize) catch @panic("alloc failed");
    rc.* = 1;
    return Obj{ .data = @ptrCast(p), .vtable = @ptrCast(&EMPTY_VT), .rc = rc, .drop_fn = null };
}

/// Create a list from a slice as Obj.
pub fn make_list_from(comptime T: type, items: []const T) Obj {
    const alloc = std.heap.page_allocator;
    const p = alloc.create(std.ArrayList(T)) catch @panic("alloc failed");
    p.* = std.ArrayList(T).init(alloc);
    p.appendSlice(items) catch {};
    const rc = alloc.create(usize) catch @panic("alloc failed");
    rc.* = 1;
    return Obj{ .data = @ptrCast(p), .vtable = @ptrCast(&EMPTY_VT), .rc = rc, .drop_fn = null };
}

/// Empty list (Obj).
pub fn empty_list() Obj {
    return make_list(i64);
}

/// bytearray(size) — Obj wrapping ArrayList(u8) with zero-fill.
pub fn bytearray(size: anytype) Obj {
    const alloc = std.heap.page_allocator;
    const n: usize = if (@TypeOf(size) == usize) size else @intCast(size);
    const p = alloc.create(std.ArrayList(u8)) catch @panic("alloc failed");
    p.* = std.ArrayList(u8).initCapacity(alloc, n) catch std.ArrayList(u8).init(alloc);
    p.appendNTimes(0, n) catch {};
    const rc = alloc.create(usize) catch @panic("alloc failed");
    rc.* = 1;
    return Obj{ .data = @ptrCast(p), .vtable = @ptrCast(&EMPTY_VT), .rc = rc, .drop_fn = null };
}

/// Copy bytes/bytearray Obj as an independent ArrayList(u8).
pub fn bytes_copy(src: Obj) Obj {
    const alloc = std.heap.page_allocator;
    const src_list: *std.ArrayList(u8) = @ptrCast(@alignCast(src.data));
    const p = alloc.create(std.ArrayList(u8)) catch @panic("alloc failed");
    p.* = std.ArrayList(u8).init(alloc);
    p.ensureTotalCapacity(src_list.items.len) catch {};
    p.appendSlice(src_list.items) catch {};
    const rc = alloc.create(usize) catch @panic("alloc failed");
    rc.* = 1;
    return Obj{ .data = @ptrCast(p), .vtable = @ptrCast(&EMPTY_VT), .rc = rc, .drop_fn = null };
}

/// Convert list[i64] to list[u8] (Python bytes(list) semantics).
pub fn list_to_bytes(src: Obj) Obj {
    const alloc = std.heap.page_allocator;
    const int_list: *std.ArrayList(i64) = @ptrCast(@alignCast(src.data));
    const p = alloc.create(std.ArrayList(u8)) catch @panic("alloc failed");
    p.* = std.ArrayList(u8).init(alloc);
    p.ensureTotalCapacity(int_list.items.len) catch {};
    for (int_list.items) |v| {
        p.append(@intCast(v & 0xFF)) catch {};
    }
    const rc = alloc.create(usize) catch @panic("alloc failed");
    rc.* = 1;
    return Obj{ .data = @ptrCast(p), .vtable = @ptrCast(&EMPTY_VT), .rc = rc, .drop_fn = null };
}

/// Append a value to an Obj-managed list.
pub fn list_append(obj: Obj, comptime T: type, value: T) void {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    p.append(value) catch {};
}

/// Get an element from an Obj-managed list (supports negative indices).
pub fn list_get(obj: Obj, comptime T: type, idx: i64) T {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    const len: i64 = @intCast(p.items.len);
    const real_idx: usize = @intCast(if (idx < 0) idx + len else idx);
    return p.items[real_idx];
}

/// Set an element in an Obj-managed list (supports negative indices).
pub fn list_set(obj: Obj, comptime T: type, idx: i64, value: T) void {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    const len: i64 = @intCast(p.items.len);
    const real_idx: usize = @intCast(if (idx < 0) idx + len else idx);
    p.items[real_idx] = value;
}

/// Get the length of an Obj-managed list.
pub fn list_len(obj: Obj, comptime T: type) i64 {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    return @as(i64, @intCast(p.items.len));
}

/// Get the items slice of an Obj-managed list (for iteration).
pub fn list_items(obj: Obj, comptime T: type) []T {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    return p.items;
}

/// Pop the last element from an Obj-managed list (Python list.pop()).
pub fn list_pop(obj: Obj, comptime T: type) T {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    return p.pop();
}

/// Remove the last element from an Obj-managed list (void variant for pop without return).
pub fn list_pop_void(obj: Obj, comptime T: type) void {
    const p: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    _ = p.pop();
}

/// Append a slice to an Obj-managed list.
pub fn list_extend(obj: Obj, comptime T: type, src: Obj) void {
    const dst: *std.ArrayList(T) = @ptrCast(@alignCast(obj.data));
    const s: *std.ArrayList(T) = @ptrCast(@alignCast(src.data));
    dst.appendSlice(s.items) catch {};
}

/// Empty vtable placeholder for containers.
const EMPTY_VT = struct {};

// ─── String operations ───

/// String index: str[i] → single-char slice (Python semantics).
pub fn str_index(s: []const u8, idx: i64) []const u8 {
    const len: i64 = @intCast(s.len);
    const real: usize = @intCast(if (idx < 0) idx + len else idx);
    return s[real .. real + 1];
}

/// String slice: str[start:end] → sub-slice (Python semantics).
pub fn str_slice(s: []const u8, start: i64, end: i64) []const u8 {
    const len: i64 = @intCast(s.len);
    var s0 = if (start < 0) start + len else start;
    var e0 = if (end < 0) end + len else end;
    if (s0 < 0) s0 = 0;
    if (e0 > len) e0 = len;
    if (s0 >= e0) return "";
    return s[@intCast(s0)..@intCast(e0)];
}

/// Python str.isdigit() — check if single char is a digit.
pub fn char_isdigit(s: []const u8) bool {
    if (s.len == 0) return false;
    return s[0] >= '0' and s[0] <= '9';
}

/// Python str.isalpha() — check if single char is alphabetic.
pub fn char_isalpha(s: []const u8) bool {
    if (s.len == 0) return false;
    const c = s[0];
    return (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z');
}

/// Parse integer from string (Python int(s)).
pub fn str_to_int(s: []const u8) i64 {
    var result: i64 = 0;
    var neg = false;
    var i: usize = 0;
    if (i < s.len and (s[i] == '-' or s[i] == '+')) {
        neg = s[i] == '-';
        i += 1;
    }
    while (i < s.len) : (i += 1) {
        const c = s[i];
        if (c < '0' or c > '9') break;
        result = result * 10 + @as(i64, c - '0');
    }
    return if (neg) -result else result;
}

/// HashMap get with default value.
pub fn dict_get_default(comptime V: type, map: std.StringHashMap(V), key: []const u8, default: V) V {
    return map.get(key) orelse default;
}

/// Slice (stub — kept for backward compat, prefer str_slice).
pub fn slice(lower: anytype, upper: anytype) void {
    _ = lower;
    _ = upper;
    return;
}

/// Legacy list_from (backward compat — returns Obj now).
pub fn list_from(comptime T: type, items: []const T) Obj {
    return make_list_from(T, items);
}

/// list_from_any is no longer used; tuple-element lists are expanded to
/// make_list + list_append sequences by the emitter.

/// time.perf_counter() — seconds since arbitrary epoch.
pub fn perf_counter() f64 {
    const ns = std.time.nanoTimestamp();
    return @as(f64, @floatFromInt(ns)) / 1_000_000_000.0;
}

/// File handle (wraps std.fs.File as integer handle).
pub fn file_open(path: []const u8) PyObject {
    const alloc = std.heap.page_allocator;
    // Ensure parent directories exist (Python open() creates files but expects dirs)
    if (std.mem.lastIndexOfScalar(u8, path, '/')) |sep| {
        const dir_path = path[0..sep];
        if (dir_path.len > 0) {
            std.fs.cwd().makePath(dir_path) catch {};
        }
    }
    const p = alloc.create(std.fs.File) catch @panic("alloc failed");
    p.* = std.fs.cwd().createFile(path, .{}) catch @panic("file open failed");
    return @as(PyObject, @intCast(@intFromPtr(p)));
}

pub fn file_write(handle: PyObject, data: anytype) void {
    const p: *std.fs.File = @ptrFromInt(@as(usize, @intCast(handle)));
    const T = @TypeOf(data);
    if (T == Obj) {
        // Obj wrapping ArrayList — write as bytes
        file_write_obj(p, data);
    } else if (@typeInfo(T) == .pointer) {
        p.writeAll(data) catch {};
    }
}

fn file_write_obj(p: *std.fs.File, obj: Obj) void {
    // Obj is always ArrayList(u8) from list_to_bytes / bytearray
    const al: *std.ArrayList(u8) = @ptrCast(@alignCast(obj.data));
    if (al.items.len > 0) {
        p.writeAll(al.items) catch {};
    }
}

pub fn file_close(handle: PyObject) void {
    const p: *std.fs.File = @ptrFromInt(@as(usize, @intCast(handle)));
    p.close();
}
