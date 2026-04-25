#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#ifdef __unix__
#include <sys/wait.h>
#endif

#include "core/py_runtime.h"
#include "std/subprocess.h"

namespace {
str _subprocess_quote(const str& value) {
    str out = str("'");
    for (char ch : value) {
        if (ch == '\'') {
            out += str("'\\''");
        } else {
            out += str(1, ch);
        }
    }
    out += str("'");
    return out;
}

int64 _subprocess_exit_code(int raw_code) {
#ifdef __unix__
    if (WIFEXITED(raw_code)) {
        return static_cast<int64>(WEXITSTATUS(raw_code));
    }
#endif
    return static_cast<int64>(raw_code);
}

str _read_file_text(const char* path) {
    ::std::ifstream in(path);
    ::std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}
}

CompletedProcess::CompletedProcess(int64 returncode, const str& stdout, const str& stderr) {
    this->returncode = returncode;
    this->stdout = stdout;
    this->stderr = stderr;
}

CompletedProcess run(const Object<list<str>>& cmd, const str& cwd, bool capture_output, const Object<dict<str, str>>& env) {
    str command;
    if (py_len(env) > int64(0)) {
        bool first_env = true;
        for (const auto& kv : *env) {
            if (!first_env) {
                command += str(" ");
            }
            first_env = false;
            command += kv.first;
            command += str("=");
            command += _subprocess_quote(kv.second);
        }
        command += str(" ");
    }
    if (cwd != str("")) {
        command += str("cd ");
        command += _subprocess_quote(cwd);
        command += str(" && ");
    }
    bool first = true;
    for (const auto& part : *cmd) {
        if (!first) {
            command += str(" ");
        }
        first = false;
        command += _subprocess_quote(part);
    }
    const char* stdout_path = "/tmp/pytra_subprocess_stdout.txt";
    const char* stderr_path = "/tmp/pytra_subprocess_stderr.txt";
    if (capture_output) {
        command += str(" > ") + str(stdout_path) + str(" 2> ") + str(stderr_path);
    }
    int raw = ::std::system(command.c_str());
    str stdout_text;
    str stderr_text;
    if (capture_output) {
        stdout_text = _read_file_text(stdout_path);
        stderr_text = _read_file_text(stderr_path);
    }
    return CompletedProcess(_subprocess_exit_code(raw), stdout_text, stderr_text);
}
