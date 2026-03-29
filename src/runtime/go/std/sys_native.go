// sys_native.go: native extern delegates for pytra.std.sys.
package main

import (
	"os"
)

var py_argv *PyList[string] = PyListFromSlice(append([]string{}, os.Args...))
var py_path *PyList[string] = NewPyList[string]()

func py_exit(code int64) {
	os.Exit(int(code))
}

func py_set_argv(values *PyList[string]) {
	py_argv = PyListFromSlice(append([]string{}, values.items...))
}

func py_set_path(values *PyList[string]) {
	py_path = PyListFromSlice(append([]string{}, values.items...))
}

func py_write_stderr(text string) {
	_, _ = os.Stderr.WriteString(text)
}

func py_write_stdout(text string) {
	_, _ = os.Stdout.WriteString(text)
}
