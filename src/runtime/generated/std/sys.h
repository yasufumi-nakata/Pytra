// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/std/sys.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_SYS_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_SYS_H

#include "runtime/cpp/core/py_types.h"

namespace pytra::std::sys {

extern list<str> argv;
extern list<str> path;

void exit(int64 code = 0);
void set_argv(const rc<list<str>>& values);
void set_path(const rc<list<str>>& values);
void write_stderr(const str& text);
void write_stdout(const str& text);

}  // namespace pytra::std::sys

using namespace pytra::std::sys;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_SYS_H
