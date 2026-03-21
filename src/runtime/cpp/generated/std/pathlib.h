// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/std/pathlib.py
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA_GENERATED_STD_PATHLIB_H
#define PYTRA_GENERATED_STD_PATHLIB_H

#include "runtime/cpp/core/py_runtime.h"

#include "std/glob.h"
#include "std/os.h"
#include "std/os_path.h"
#include "runtime/cpp/core/exceptions.h"

namespace pytra::std::pathlib {

struct Path;

    struct Path {
        str _value;
        
        Path(const object& value);
        str __str__() const;
        str __repr__() const;
        str __fspath__() const;
        Path __truediv__(const object& rhs) const;
        Path parent() const;
        Object<list<Path>> parents() const;
        str name() const;
        str suffix() const;
        str stem() const;
        Path with_suffix(const str& suffix) const;
        Path relative_to(const object& other) const;
        Path resolve() const;
        bool exists() const;
        void mkdir(bool parents = false, bool exist_ok = false) const;
        str read_text(const str& encoding = "utf-8") const;
}  // namespace pytra::std::pathlib

    Path::Path(const object& value) {
            if (false)
                this->_value = py_to_string((object(value.as<Path>())).as<Path>()->_value);
            else
                this->_value = value.unbox<str, PYTRA_TID_STR>();
    }

    str Path::__str__() const {
            return this->_value;
    }

    str Path::__repr__() const {
            return "Path(" + this->_value + ")";
    }

    str Path::__fspath__() const {
            return this->_value;
    }

    Path Path::__truediv__(const object& rhs) const {
            if (false)
                return Path(pytra::std::os_path::join(this->_value, (object(rhs.as<Path>())).as<Path>()->_value));
            return Path(pytra::std::os_path::join(this->_value, rhs.unbox<str, PYTRA_TID_STR>()));
    }

    Path Path::parent() const {
            auto parent_txt = pytra::std::os_path::dirname(this->_value);
            if (parent_txt == "")
                parent_txt = ".";
            return Path(parent_txt);
    }

    Object<list<Path>> Path::parents() const {
            Object<list<Path>> out = rc_list_from_value(list<Path>{});
            str current = py_to_string(pytra::std::os_path::dirname(this->_value));
            while (true) {
                if (current == "")
                    current = ".";
                rc_list_ref(out).append(Path(current));
                str next_current = py_to_string(pytra::std::os_path::dirname(current));
                if (next_current == "")
                    next_current = ".";
                if (next_current == current)
                    break;
                current = next_current;
            }
            return out;
    }

    str Path::name() const {
            return pytra::std::os_path::basename(this->_value);
    }

    str Path::suffix() const {
            auto __tuple_1 = pytra::std::os_path::splitext(pytra::std::os_path::basename(this->_value));
            auto _ = py_at(__tuple_1, 0);
            auto ext = py_at(__tuple_1, 1);
            return ext;
    }

    str Path::stem() const {
            auto __tuple_2 = pytra::std::os_path::splitext(pytra::std::os_path::basename(this->_value));
            auto root = py_at(__tuple_2, 0);
            auto _ = py_at(__tuple_2, 1);
            return root;
    }

    Path Path::with_suffix(const str& suffix) const {
            str root;
            str _ext;
            auto __tuple_3 = pytra::std::os_path::splitext(this->_value);
            root = py_at(__tuple_3, 0);
            _ext = py_at(__tuple_3, 1);
            return Path(root + suffix);
    }

    Path Path::relative_to(const object& other) const {
            str base;
            if (false)
                base = py_to_string((object(other.as<Path>())).as<Path>()->_value);
            else
                base = other.unbox<str, PYTRA_TID_STR>();
            str self_abs = py_to_string(pytra::std::os_path::abspath(this->_value));
            str base_abs = py_to_string(pytra::std::os_path::abspath(base));
            if (!(py_endswith(base_abs, "/")))
                base_abs = base_abs + "/";
            if ((self_abs == base_abs) || (self_abs == py_str_slice(base_abs, 0, -(1))))
                return Path(".");
            if (py_startswith(self_abs, base_abs))
                return Path(py_str_slice(self_abs, base_abs.size(), int64(self_abs.size())));
            throw ValueError(this->_value + " is not relative to " + base);
    }

    Path Path::resolve() const {
            return Path(pytra::std::os_path::abspath(this->_value));
    }

    bool Path::exists() const {
            return pytra::std::os_path::exists(this->_value);
    }

    void Path::mkdir(bool parents, bool exist_ok) const {
            if (parents) {
                pytra::std::os::makedirs(this->_value, exist_ok);
                return;
            }
            if ((exist_ok) && (pytra::std::os_path::exists(this->_value)))
                return;
            pytra::std::os::mkdir(this->_value);
    }

        str read_text(const str& encoding = "utf-8") const {
            pytra::runtime::cpp::base::PyFile f = open(this->_value, "r");
            {
                auto __finally_4 = py_make_scope_exit([&]() {{
                    f.close();
                });
                return f.read();
            }
        }
        int64 write_text(const str& text, const str& encoding = "utf-8") const {
            pytra::runtime::cpp::base::PyFile f = open(this->_value, "w");
            {
                auto __finally_5 = py_make_scope_exit([&]() {{
                    f.close();
                });
                return f.write(text);
            }
        }
        Path joinpath(const Object<list<object>>& parts) const {
            str result = this->_value;
            for (object part : rc_list_ref(parts)) {
                if (false)
                    result = py_to_string(pytra::std::os_path::join(result, (object(part.as<Path>())).as<Path>()->_value));
                else
                    result = py_to_string(pytra::std::os_path::join(result, part.unbox<str, PYTRA_TID_STR>()));
            }
            return Path(result);
        }
        Object<list<Path>> glob(const str& pattern) const {
            Object<list<str>> paths = py_to<Object<list<str>>>(pytra::std::glob::glob(pytra::std::os_path::join(this->_value, pattern)));
            Object<list<Path>> out = rc_list_from_value(list<Path>{});
            for (str p : rc_list_ref(paths)) {
                rc_list_ref(out).append(Path(p));
            }
            return out;
        }
        static Path cwd() {
            return Path(pytra::std::os::getcwd());
        }
    };
    


}  // namespace pytra::std::pathlib

#endif  // PYTRA_GENERATED_STD_PATHLIB_H
