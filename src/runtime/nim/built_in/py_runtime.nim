# Nim runtime for Pytra
import std/os
import std/times
import std/tables
import std/strutils
import std/math

proc py_perf_counter*(): float =
  epochTime()

# Pytra built-ins
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
  $v

proc py_isdigit*(v: char): bool =
  v.isDigit()

proc py_isdigit*(v: string): bool =
  v.len > 0 and v[0].isDigit()

proc py_isalpha*(v: char): bool =
  v.isAlphaAscii()

proc py_isalpha*(v: string): bool =
  v.len > 0 and v[0].isAlphaAscii()

proc py_len*(v: seq or string or Table): int =
  v.len

template py_truthy*(v: auto): bool =
  when v is bool:
    v
  elif v is int or v is float:
    v != 0
  elif v is string or v is seq or v is Table:
    v.len > 0
  else:
    not v.isNil

# Python-style modulo
proc py_mod*[T: int or float](a, b: T): T =
  if b == 0:
    return 0
  let r = a mod b
  if (r > 0 and b < 0) or (r < 0 and b > 0):
    r + b
  else:
    r

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

# Binary file I/O helpers
proc py_write_bytes*(f: File, data: seq[uint8]) =
  ## Write raw bytes to a file (binary mode).
  if data.len > 0:
    discard f.writeBuffer(unsafeAddr data[0], data.len)

proc py_write_bytes*(f: File, data: seq[int]) =
  ## Write seq[int] as raw bytes to a file (binary mode).
  if data.len > 0:
    var buf = newSeq[uint8](data.len)
    for i in 0 ..< data.len:
      buf[i] = uint8(data[i] and 0xFF)
    discard f.writeBuffer(unsafeAddr buf[0], buf.len)

include "image_runtime.nim"
