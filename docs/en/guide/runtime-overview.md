<a href="../../ja/guide/runtime-overview.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# How the Runtime Works

Pytra's generated code works in combination with runtime helpers in the target language. This page explains how memory management, containers, and built-in functions operate.

## Memory Management: Reference Counting (RC)

Pytra manages memory using **Reference Counting (RC)**. It does not use a GC (Garbage Collector).

```
Object<Circle>
  +----------------+
  | ptr -----------+---> Circle { radius: 5.0 }
  | rc  -----------+---> ControlBlock { ref_count: 2, type_id: 1003 }
  +----------------+
```

- `Object<T>` is a smart pointer with reference counting
- Copying increments the reference count
- Leaving a scope decrements the reference count
- When the reference count reaches 0, the object is freed

Unlike Python's GC, circular references are not detected. Pytra code is designed with the assumption that circular references are avoided.

## Container Reference Semantics

Python's `list` / `dict` / `set` are reference types. When passed to a function and modified, the changes are reflected at the call site.

```python
def add_item(xs: list[int], v: int) -> None:
    xs.append(v)

items: list[int] = [1, 2, 3]
add_item(items, 4)
print(items)  # [1, 2, 3, 4] -- the change is reflected
```

To faithfully reproduce this behavior, Pytra wraps containers in **reference-type wrappers**.

| Language | Typing | GC | list Type | Pytra Memory Management |
|---|---|---|---|---|
| C++ | Static | None | `Object<list<int64>>` | Manual RC |
| Rust | Static | None | `Rc<RefCell<Vec<i64>>>` | Manual RC + interior mutability |
| Go | Static | Yes | `*PyList[int64]` | GC handles it (pointer sharing) |
| Java | Static | Yes | `ArrayList<Long>` | GC handles it (reference types by default) |
| C# | Static | Yes | `List<long>` | GC handles it (reference types by default) |
| Swift | Static | ARC | class wrapper | ARC (compiler-inserted RC) |
| JS/TS | Dynamic | Yes | `Array` | GC handles it (everything is reference) |
| Ruby/Lua/PHP | Dynamic | Yes | Native array | GC handles it |

RC is only needed for **C++ and Rust**, which have no GC. All other languages have GC or ARC, so Pytra does not need to manage memory manually.

### Degeneracy to Value Types

When escape analysis proves that "this variable does not escape the function," the reference wrapper can be removed and the value can be held as a value type.

```python
def sum_list(n: int) -> int:
    buf: list[int] = []      # buf is only used within this function
    i: int = 0
    while i < n:
        buf.append(i)
        i += 1
    total: int = 0
    for x in buf:
        total += x
    return total
```

Through the linker's `container_value_locals_v1` hint, `buf` is held as a value type (`[]int64` / `vector<int64>`). This improves memory efficiency.

## Built-in Functions

Built-in functions like `len`, `print`, `str`, `int`, `float` are defined in `pytra/built_in/`.

```python
print("hello")        # -> __pytra_py_print("hello")
x = len(items)         # -> __pytra_py_len(items)
s = str(42)            # -> __pytra_py_to_string(42)
```

Function name conversions are defined in the `calls` map of `mapping.json`. The emitter never hardcodes them.

## Exception Classes

Exception classes are defined in pure Python in `pytra/built_in/error.py`.

```
PytraError
+-- BaseException
    +-- Exception
        +-- ValueError
        +-- RuntimeError
        +-- TypeError
        +-- IndexError
        +-- KeyError
        +-- ...
```

They can be used directly without import (since they are built_in). They are automatically converted to all languages through the pipeline, so no handwritten runtime per language is needed.

## stdlib Modules

Alternatives to the Python standard library are implemented in pure Python in `pytra/std/`.

```python
from pytra.std import math
from pytra.std import json
from pytra.std.pathlib import Path
```

These are also converted to all languages through the pipeline. Only a few low-level functions (such as file I/O) are delegated to each language's native runtime.

## Image Output

PNG/GIF writing is implemented in pure Python in `pytra/utils/png.py` and `pytra/utils/gif.py`. The encoding core (CRC32, Adler32, DEFLATE, LZW) is also entirely written in Python and converted through the pipeline.

```python
from pytra.utils.png import write_rgb_png

pixels: list[int] = [0] * (256 * 256 * 3)
# ... write pixels ...
write_rgb_png("output.png", 256, 256, pixels)
```

## Detailed Specifications

- [Runtime Specification](../spec/spec-runtime.md)
- [GC Specification](../spec/spec-gc.md)
- [Boxing/Unboxing Specification](../spec/spec-boxing.md)
- [Emitter Guidelines S10](../spec/spec-emitter-guide.md) -- container reference semantics
