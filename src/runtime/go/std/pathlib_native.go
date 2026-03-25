// pathlib_native.go: @extern delegation for pytra.std.pathlib.
// Hand-written native implementation.
package main

import (
	"os"
	"path/filepath"
)

func Path(s string) string { return s }
func py_Path(s string) string { return s }

func py_pathlib_write_text(path string, content string) {
	dir := filepath.Dir(path)
	if dir != "" && dir != "." { os.MkdirAll(dir, 0755) }
	os.WriteFile(path, []byte(content), 0644)
}
