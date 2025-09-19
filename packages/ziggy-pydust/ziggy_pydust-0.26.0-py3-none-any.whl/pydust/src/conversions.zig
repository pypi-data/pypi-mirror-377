// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//         http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

const py = @import("./pydust.zig");
const tramp = @import("./trampoline.zig");
const pytypes = @import("./pytypes.zig");
const State = @import("./discovery.zig").State;

/// Zig PyObject-like -> ffi.PyObject. Convert a Zig PyObject-like value into a py.PyObject.
///  e.g. py.PyObject, py.PyTuple, ffi.PyObject, etc.
pub inline fn object(comptime root: type, value: anytype) py.PyObject {
    return tramp.Trampoline(root, @TypeOf(value)).asObject(value);
}

/// Zig -> Python. Return a Python representation of a Zig object.
/// For Zig primitives, this constructs a new Python object.
/// For PyObject-like values, this returns the value without creating a new reference.
pub inline fn createOwned(comptime root: type, value: anytype) py.PyError!py.PyObject {
    const trampoline = tramp.Trampoline(root, @TypeOf(value));
    defer trampoline.decref_objectlike(value);
    return trampoline.wrap(value);
}

/// Zig -> Python. Convert a Zig object into a Python object. Returns a new object.
pub inline fn create(comptime root: type, value: anytype) py.PyError!py.PyObject {
    return tramp.Trampoline(root, @TypeOf(value)).wrap(value);
}

/// Python -> Zig. Return a Zig object representing the Python object.
pub inline fn as(comptime root: type, comptime T: type, obj: anytype) py.PyError!T {
    return tramp.Trampoline(root, T).unwrap(object(root, obj));
}

/// Python -> Pydust. Perform an unchecked cast from a PyObject to a given PyDust class type.
pub inline fn unchecked(comptime root: type, comptime T: type, obj: py.PyObject) T {
    const Definition = @typeInfo(T).pointer.child;
    const definition = State.getDefinition(root, Definition);
    if (definition.type != .class) {
        @compileError("Can only perform unchecked cast into a PyDust class type. Found " ++ @typeName(Definition));
    }
    const instance: *pytypes.PyTypeStruct(Definition) = @ptrCast(@alignCast(obj.py));
    return &instance.state;
}

const testing = @import("std").testing;
const expect = testing.expect;

test "as py -> zig" {
    py.initialize();
    defer py.finalize();

    const root = @This();

    // Start with a Python object
    const str = try py.PyString.create("hello");
    try expect(py.refcnt(root, str) == 1);

    // Return a slice representation of it, and ensure the refcnt is untouched
    _ = try py.as(root, []const u8, str);
    try expect(py.refcnt(root, str) == 1);

    // Return a PyObject representation of it, and ensure the refcnt is untouched.
    _ = try py.as(root, py.PyObject, str);
    try expect(py.refcnt(root, str) == 1);
}

test "create" {
    py.initialize();
    defer py.finalize();

    const root = @This();

    const str = try py.PyString.create("Hello");
    try testing.expectEqual(@as(isize, 1), py.refcnt(root, str));

    const some_tuple = try py.create(root, .{str});
    defer some_tuple.decref();
    try testing.expectEqual(@as(isize, 2), py.refcnt(root, str));

    str.obj.decref();
    try testing.expectEqual(@as(isize, 1), py.refcnt(root, str));
}

test "createOwned" {
    py.initialize();
    defer py.finalize();

    const root = @This();

    const str = try py.PyString.create("Hello");
    try testing.expectEqual(@as(isize, 1), py.refcnt(root, str));

    const some_tuple = try py.createOwned(root, .{str});
    defer some_tuple.decref();
    try testing.expectEqual(@as(isize, 1), py.refcnt(root, str));
}
