# Nim runtime for Pytra
import std/os
import std/times
import std/tables
import std/strutils
import std/math
import std/sequtils
import std/sets
import std/algorithm

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
type PyObj* = ref RootObj
type PyPath* = string
type PyFile* = File

template py_instanceof*(v: typed, T: typedesc): bool =
  when compiles(v of T):
    v of T
  elif compiles(v is T):
    v is T
  else:
    false

template py_is_dict*(v: typed): bool =
  when v is Table:
    true
  else:
    false

template py_is_list*(v: typed): bool =
  when v is seq:
    true
  else:
    false

template py_is_str*(v: typed): bool =
  when v is string:
    true
  else:
    false

template py_is_int*(v: typed): bool =
  when v is SomeInteger:
    true
  else:
    false

template py_is_bool*(v: typed): bool =
  when v is bool:
    true
  else:
    false

template py_is_float*(v: typed): bool =
  when v is SomeFloat:
    true
  else:
    false

proc py_open*(path: string, mode: string): PyFile =
  var f: File
  var file_mode = fmRead
  if mode == "wb":
    file_mode = fmWrite
  elif mode == "ab":
    file_mode = fmAppend
  elif mode == "rb":
    file_mode = fmRead
  if not open(f, path, file_mode):
    raise newException(IOError, "failed to open file: " & path)
  return f

proc write*(f: var PyFile, data: seq[uint8]): int =
  if data.len > 0:
    discard writeBytes(f, data, 0, data.len)
  return data.len

proc close*(f: var PyFile) =
  system.close(f)

proc py_to_string*(v: auto): string

# ---------------------------------------------------------------------------
# Print
# ---------------------------------------------------------------------------
var py_capture_stdout_active = false
var py_capture_stdout_lines: seq[string] = @[]

proc py_print*() =
  if py_capture_stdout_active:
    py_capture_stdout_lines.add("")
  else:
    echo ""

proc py_print*(args: varargs[string, py_to_string]) =
  var parts: seq[string] = @[]
  for a in args:
    parts.add(a)
  let line = parts.join(" ")
  if py_capture_stdout_active:
    py_capture_stdout_lines.add(line)
  else:
    echo line

# ---------------------------------------------------------------------------
# Conversions
# ---------------------------------------------------------------------------
proc py_perf_counter*(): float =
  epochTime()

proc py_int*(v: auto): int =
  when v is string:
    parseInt(v)
  else:
    int(v)

proc py_float*(v: auto): float =
  when v is string:
    parseFloat(v)
  else:
    float(v)

proc py_str*(v: auto): string =
  when v is bool:
    if v: "True" else: "False"
  elif v is typeof(nil):
    "None"
  elif v is ref CatchableError:
    if v.isNil: "" else: v.msg
  else:
    $v

proc py_to_string*(v: auto): string =
  when v is bool:
    if v: "True" else: "False"
  elif v is typeof(nil):
    "None"
  elif v is ref CatchableError:
    if v.isNil: "" else: v.msg
  else:
    $v

proc py_bool*(v: auto): bool =
  when v is bool:
    v
  elif v is int or v is float:
    v != 0
  elif v is string:
    v.len > 0
  else:
    not v.isNil

proc py_ord*(c: string): int =
  if c.len > 0: int(c[0]) else: 0

proc py_chr*(i: int): string =
  $chr(i)

# ---------------------------------------------------------------------------
# String methods
# ---------------------------------------------------------------------------
proc py_str_strip*(s: string): string = s.strip()
proc py_str_lstrip*(s: string): string = s.strip(trailing = false)
proc py_str_rstrip*(s: string): string = s.strip(leading = false)
proc py_str_startswith*(s: string, prefix: string): bool = s.startsWith(prefix)
proc py_str_endswith*(s: string, suffix: string): bool = s.endsWith(suffix)
proc py_str_replace*(s: string, old: string, new_str: string): string = s.replace(old, new_str)
proc py_str_find*(s: string, sub: string): int = s.find(sub)
proc py_str_rfind*(s: string, sub: string): int =
  var last = -1
  var pos = 0
  while pos < s.len:
    let found = s.find(sub, pos)
    if found < 0: break
    last = found
    pos = found + 1
  return last
proc py_str_split*(s: string): seq[string] = s.splitWhitespace()
proc py_str_split*(s: string, sep: string): seq[string] = s.split(sep)
proc py_str_join*(sep: string, items: seq[string]): string = items.join(sep)
proc py_str_upper*(s: string): string = s.toUpperAscii()
proc py_str_lower*(s: string): string = s.toLowerAscii()
proc py_str_count*(s: string, sub: string): int = s.count(sub)
proc py_str_index*(s: string, sub: string): int =
  let i = s.find(sub)
  if i < 0: raise newException(ValueError, "substring not found")
  return i
proc py_str_isdigit*(s: string): bool = s.len > 0 and s.allCharsInSet(Digits)
proc py_str_isalpha*(s: string): bool = s.len > 0 and s.allCharsInSet(Letters)
proc py_str_isalnum*(s: string): bool = s.len > 0 and s.allCharsInSet(Letters + Digits)
proc py_str_isspace*(s: string): bool = s.len > 0 and s.allCharsInSet(Whitespace)

proc py_isdigit*(v: char): bool = v.isDigit()
proc py_isdigit*(v: string): bool = v.len > 0 and v[0].isDigit()
proc py_isalpha*(v: char): bool = v.isAlphaAscii()
proc py_isalpha*(v: string): bool = v.len > 0 and v[0].isAlphaAscii()

# ---------------------------------------------------------------------------
# Builtins
# ---------------------------------------------------------------------------
proc py_len*(v: string): int = v.len
proc py_len*[T](v: seq[T]): int = v.len
proc py_len*[K, V](v: Table[K, V]): int = v.len
proc py_len*[T](v: HashSet[T]): int = v.len

template py_truthy*(v: auto): bool =
  when v is bool:
    v
  elif v is SomeInteger or v is SomeFloat:
    v != 0
  elif v is string or v is seq or v is Table or v is HashSet:
    v.len > 0
  else:
    not v.isNil

proc py_round*(v: float64): int64 = int64(round(v))
proc py_round*(v: float64, ndigits: int): float64 =
  let factor = pow(10.0, float64(ndigits))
  round(v * factor) / factor

proc py_sum*[T](items: seq[T]): T =
  var total: T = T(0)
  for item in items:
    total += item
  return total

proc py_sorted*[T](items: seq[T]): seq[T] =
  var copy = items
  copy.sort()
  return copy

proc py_reversed*[T](items: seq[T]): seq[T] =
  var copy = items
  copy.reverse()
  return copy

proc py_enumerate*[T](items: seq[T]): seq[(int, T)] =
  var result_seq: seq[(int, T)] = @[]
  var i = 0
  for item in items:
    result_seq.add((i, item))
    i += 1
  return result_seq

proc py_enumerate*[T](items: seq[T], start: int): seq[(int, T)] =
  var result_seq: seq[(int, T)] = @[]
  var i = start
  for item in items:
    result_seq.add((i, item))
    i += 1
  return result_seq

proc py_in*[T](item: T, items: seq[T]): bool = item in items
proc py_in*(item: string, items: string): bool = item in items

# ---------------------------------------------------------------------------
# Math
# ---------------------------------------------------------------------------
proc py_floordiv*(a, b: int64): int64 =
  if b == 0: raise newException(DivByZeroDefect, "integer division by zero")
  let d = a div b
  if (a xor b) < 0 and d * b != a:
    return d - 1
  return d

proc py_mod*[T: int64 | float64](a, b: T): T =
  if b == T(0): return T(0)
  let r = a mod b
  if (r > T(0) and b < T(0)) or (r < T(0) and b > T(0)):
    r + b
  else:
    r

# ---------------------------------------------------------------------------
# Range iterator
# ---------------------------------------------------------------------------
iterator py_range*(start: int, stop: int, step: int): int =
  if step != 0:
    var i = start
    if step > 0:
      while i < stop:
        yield i
        i += step
    else:
      while i > stop:
        yield i
        i += step

# ---------------------------------------------------------------------------
# Container helpers
# ---------------------------------------------------------------------------
proc pop*[T](s: var seq[T]): T =
  if s.len == 0: raise newException(IndexDefect, "pop from empty list")
  result = s[s.len - 1]
  s.setLen(s.len - 1)

proc pop*[T](s: var seq[T], idx: int): T =
  if idx < 0 or idx >= s.len: raise newException(IndexDefect, "pop index out of range")
  result = s[idx]
  s.delete(idx)

# ---------------------------------------------------------------------------
# Assertions (test framework)
# ---------------------------------------------------------------------------
proc py_assert_true*(cond: bool, msg: string = ""): bool =
  if not cond:
    if msg.len > 0:
      raise newException(AssertionDefect, msg & ": assertion failed")
    raise newException(AssertionDefect, "assertion failed")
  return true

proc py_assert_eq*[T](a, b: T, msg: string = ""): bool =
  if a != b:
    let detail = if msg != "": msg & ": " else: ""
    raise newException(AssertionDefect, detail & "assertion failed: " & $a & " != " & $b)
  return true

proc py_assert_stdout*(expected: seq[string], fn: proc()): bool =
  py_capture_stdout_active = true
  py_capture_stdout_lines = @[]
  fn()
  let captured = py_capture_stdout_lines
  py_capture_stdout_active = false
  py_capture_stdout_lines = @[]
  if captured.len != expected.len:
    return false
  var i = 0
  while i < captured.len:
    if captured[i] != expected[i]:
      return false
    i += 1
  return true

proc py_assert_all*(items: seq[bool], msg: string = ""): bool =
  for item in items:
    if not item:
      let detail = if msg != "": msg & ": " else: ""
      raise newException(AssertionDefect, detail & "assert_all failed")
  return true

# ---------------------------------------------------------------------------
# Format helper
# ---------------------------------------------------------------------------
proc py_fmt*(v: auto, spec: string): string =
  # Simplified format - handle common cases
  if spec.endsWith("f"):
    let precision_str = spec[0 ..< spec.len - 1]
    if precision_str.startsWith("."):
      let prec = parseInt(precision_str[1 ..< precision_str.len])
      return formatFloat(float(v), ffDecimal, prec)
  return $v

# ---------------------------------------------------------------------------
# Binary file I/O helpers
# ---------------------------------------------------------------------------
proc py_write_bytes*(f: File, data: seq[uint8]) =
  if data.len > 0:
    discard f.writeBuffer(unsafeAddr data[0], data.len)

proc py_write_bytes*(f: File, data: seq[int]) =
  if data.len > 0:
    var buf = newSeq[uint8](data.len)
    for i in 0 ..< data.len:
      buf[i] = uint8(data[i] and 0xFF)
    discard f.writeBuffer(unsafeAddr buf[0], buf.len)

# Image functions (write_rgb_png, save_gif, grayscale_palette) are provided
# by emitter-generated utils/png.nim and utils/gif.nim modules (§6).
