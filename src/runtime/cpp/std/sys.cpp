#include "core/py_runtime.h"
#include "core/process_runtime.h"

#include "std/sys.h"

list<str> argv = py_runtime_argv();
list<str> path = {};

void exit(int64 code) {
    py_runtime_exit(code);
}

void set_argv(const list<str>& values) {
    argv = values;
    py_runtime_set_argv(values);
}

void set_path(const list<str>& values) {
    path = values;
}

void write_stderr(const str& text) {
    py_runtime_write_stderr(text);
}

void write_stdout(const str& text) {
    py_runtime_write_stdout(text);
}
