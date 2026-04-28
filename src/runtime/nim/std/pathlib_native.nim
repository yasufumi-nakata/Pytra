import std/os as std_os
import py_runtime

proc Path*(text: string): PyPath =
  text

proc Path*(value: PyObj): PyPath =
  py_str(value)

proc cwd*(): PyPath =
  std_os.getCurrentDir()

proc parent*(path: PyPath): PyPath =
  std_os.parentDir(path)

proc resolve*(path: PyPath): PyPath =
  std_os.absolutePath(path)

proc parents*(path: PyPath): seq[PyPath] =
  var current = std_os.parentDir(std_os.absolutePath(path))
  while current != "" and current != std_os.parentDir(current):
    result.add(current)
    current = std_os.parentDir(current)

proc name*(path: PyPath): string =
  std_os.extractFilename(path)

proc stem*(path: PyPath): string =
  let (_, base, _) = std_os.splitFile(path)
  base

proc mkdir*(path: PyPath): void =
  std_os.createDir(path)

proc mkdir*(path: PyPath, parents: bool, exist_ok: bool): void =
  discard parents
  discard exist_ok
  std_os.createDir(path)

proc joinpath*(path: PyPath, child: string, more: varargs[string]): PyPath =
  result = std_os.joinPath(path, child)
  for part in more:
    result = std_os.joinPath(result, part)

proc `/`*(path: PyPath, child: string): PyPath =
  std_os.joinPath(path, child)

proc exists*(path: PyPath): bool =
  std_os.fileExists(path) or std_os.dirExists(path)

proc write_text*(path: PyPath, text: string): int =
  writeFile(path, text)
  text.len

proc write_text*(path: PyPath, text: string, encoding: string): int =
  discard encoding
  writeFile(path, text)
  text.len

proc read_text*(path: PyPath): string =
  readFile(path)

proc read_text*(path: PyPath, encoding: string): string =
  discard encoding
  readFile(path)

proc read_text*(path: PyPath, encoding: string, errors: string): string =
  discard encoding
  discard errors
  readFile(path)
