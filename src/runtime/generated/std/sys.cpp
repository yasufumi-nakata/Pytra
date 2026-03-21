#include "core/py_runtime.h"
#include "core/process_runtime.h"

namespace pytra::std::sys {

    list<str> argv;
    list<str> path;
    object stderr;
    object stdout;
    
    /* pytra.std.sys: extern-marked sys API with Python runtime fallback. */
    
    void exit(int64 code = 0) {
        sys.exit(code);
    }
    
    void set_argv(const Object<list<str>>& values) {
        argv.clear();
        for (str v : rc_list_ref(values)) {
            argv.append(v);
        }
    }
    
    void set_path(const Object<list<str>>& values) {
        path.clear();
        for (str v : rc_list_ref(values)) {
            path.append(v);
        }
    }
    
    void write_stderr(const str& text) {
        sys.stderr.write(text);
    }
    
    void write_stdout(const str& text) {
        sys.stdout.write(text);
    }
    
    static void __pytra_module_init() {
        static bool __initialized = false;
        if (__initialized) return;
        __initialized = true;
        argv = py_to<Object<list<str>>>(pytra::std::extern(sys.argv));
        path = py_to<Object<list<str>>>(pytra::std::extern(sys.path));
        stderr = object(pytra::std::extern(sys.stderr));
        stdout = object(pytra::std::extern(sys.stdout));
    }
    
}  // namespace pytra::std::sys
