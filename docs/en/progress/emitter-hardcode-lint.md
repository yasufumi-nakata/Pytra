<a href="../../ja/progress/emitter-hardcode-lint.md">
  <img alt="日本語で読む" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# Emitter hardcode violation matrix

> Machine-generated file. Run `python3 tools/check/check_emitter_hardcode_lint.py` to update.
> Generated at: 2026-03-31T05:00:13
> [Links](./index.md)

Matrix of grep-detected violations where the emitter hardcodes module names, runtime symbols, or class names instead of using EAST3 data.
Fewer violations means the emitter is more faithfully following the EAST3 source of truth.

| Icon | Meaning |
|---|---|
| 🟩 | No violations |
| 🟥 | Violations found (see details below) |
| ⬜ | Not implemented (no emitter in toolchain2) |

> **js** shares the **ts** emitter and has no separate implementation; the js column mirrors ts results.

| Category | cpp | rs | cs | ps1 | js | ts | dart | go | java | swift | kotlin | ruby | lua | scala | php | nim | julia | zig |
|--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| module name | 🟩 | 🟩 | 🟩 | ⬜ | 🟥 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ |
| runtime symbol | 🟥 | 🟩 | 🟩 | ⬜ | 🟥 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ |
| target const | 🟩 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ |
| prefix match | 🟩 | 🟩 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ |
| class name | 🟥 | 🟩 | 🟥 | ⬜ | 🟥 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟥 | 🟥 | ⬜ | 🟥 | 🟥 | ⬜ | ⬜ |
| Python syntax | 🟩 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟥 | 🟩 | ⬜ | 🟩 | 🟥 | ⬜ | ⬜ |
| type_id | 🟥 | 🟩 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ |
| **🟩 PASS** | 4 | 7 | 4 | — | 4 | 4 | — | 7 | 7 | — | — | 5 | 5 | — | 6 | 5 | — | — |
| **🟥 FAIL** | 3 | — | 3 | — | 3 | 3 | — | — | — | — | — | 2 | 2 | — | 1 | 2 | — | — |
| **⬜ Not impl.** | — | — | — | 7 | — | — | 7 | — | — | 7 | 7 | — | — | 7 | — | — | 7 | 7 |

## Details

### class_name / cpp (3)

```
src/toolchain2/emit/cpp/emitter.py:73: "BaseException", "Exception", "ValueError", "TypeError", "IndexError",
src/toolchain2/emit/cpp/emitter.py:1307: if attr == "add_argument" and owner_type == "ArgumentParser":
src/toolchain2/emit/cpp/emitter.py:2665: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError") or rc == "s
```

### class_name / cs (7)

```
src/toolchain2/emit/cs/emitter.py:263: if resolved_type == "Path" and resolved_type in ctx.import_alias_modules:
src/toolchain2/emit/cs/emitter.py:573: if owner_type == "Path" and attr_name in ("parent", "parents", "name", "suffix", "stem"):
src/toolchain2/emit/cs/emitter.py:718: if func_name in ("Exception", "BaseException", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError", "Nam
src/toolchain2/emit/cs/emitter.py:807: if attr_name == "Path":
src/toolchain2/emit/cs/emitter.py:831: if func_name == "Path" and func_name in ctx.import_alias_modules:
src/toolchain2/emit/cs/emitter.py:1234: type_name = "Exception"
src/toolchain2/emit/cs/emitter.py:1590: if ctx.current_class_name == "Path" and _str(node, "name") == "joinpath":
```

### class_name / lua (5)

```
src/toolchain2/emit/lua/emitter.py:145: "Exception", "BaseException", "RuntimeError", "ValueError",
src/toolchain2/emit/lua/emitter.py:273: if owner_rt == "Path":
src/toolchain2/emit/lua/emitter.py:466: if owner_rt == "Path":
src/toolchain2/emit/lua/emitter.py:588: if op == "Div" and (left_rt == "Path" or right_rt == "Path"):
src/toolchain2/emit/lua/emitter.py:1339: if base_name != "" and base_name not in ("object", "Exception", "BaseException"):
```

### class_name / nim (1)

```
src/toolchain2/emit/nim/emitter.py:154: "Exception", "BaseException", "RuntimeError", "ValueError",
```

### class_name / php (2)

```
src/toolchain2/emit/php/emitter.py:143: "Exception", "BaseException", "RuntimeError", "ValueError",
src/toolchain2/emit/php/emitter.py:1178: if exc_rt in ("Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError"):
```

### class_name / ruby (1)

```
src/toolchain2/emit/ruby/emitter.py:131: "Exception", "RuntimeError", "ValueError", "TypeError",
```

### class_name / ts (4)

```
src/toolchain2/emit/ts/emitter.py:109: "Path", "PyPath", "py_math_tau",
src/toolchain2/emit/ts/emitter.py:112: "ArgumentParser",
src/toolchain2/emit/ts/emitter.py:232: "Exception", "BaseException", "RuntimeError", "ValueError",
src/toolchain2/emit/ts/emitter.py:1987: _BUILTIN_EXC_MAP["Exception"] = "Error"
```

### module_name / ts (1)

```
src/toolchain2/emit/ts/emitter.py:116: "sys", "pyset_argv", "pyset_path",
```

### prefix_match / cs (3)

```
src/toolchain2/emit/cs/emitter.py:140: module_id[len("pytra.std."):] if module_id.startswith("pytra.std.") else "",
src/toolchain2/emit/cs/emitter.py:141: module_id[len("pytra.built_in."):] if module_id.startswith("pytra.built_in.") else "",
src/toolchain2/emit/cs/emitter.py:163: if module_id.startswith("pytra.std."):
```

### prefix_match / lua (2)

```
src/toolchain2/emit/lua/emitter.py:1645: if module_id.startswith("pytra.built_in."):
src/toolchain2/emit/lua/emitter.py:1730: if isinstance(module_id, str) and module_id.startswith("pytra.built_in."):
```

### python_syntax / nim (1)

```
src/toolchain2/emit/nim/emitter.py:891: if attr == "__init__" and isinstance(owner_node, dict) and _str(owner_node, "repr") == "super()":
```

### python_syntax / ruby (2)

```
src/toolchain2/emit/ruby/emitter.py:757: if isinstance(owner_node, dict) and _str(owner_node, "repr") == "super()":
src/toolchain2/emit/ruby/emitter.py:1644: _emit(ctx, "super()")
```

### runtime_symbol / cpp (1)

```
src/toolchain2/emit/cpp/emitter.py:1532: if rc in ("py_print", "py_len") and len(arg_strs) >= 1:
```

### runtime_symbol / ts (1)

```
src/toolchain2/emit/ts/emitter.py:115: "perf_counter",
```

### type_id / cpp (1)

```
src/toolchain2/emit/cpp/emitter.py:2084: if tid == "" and expected_name.startswith("PYTRA_TID_"):
```

### type_id / cs (2)

```
src/toolchain2/emit/cs/emitter.py:328: if type_name.startswith("PYTRA_TID_"):
src/toolchain2/emit/cs/emitter.py:373: if ident.startswith("PYTRA_TID_"):
```
