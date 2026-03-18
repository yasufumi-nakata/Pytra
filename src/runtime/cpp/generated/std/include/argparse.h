// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/std/argparse.py
// generated-by: src/backends/cpp/cli.py

#ifndef PYTRA__TMP_ARGPARSE_FINAL_INCLUDE_ARGPARSE_H
#define PYTRA__TMP_ARGPARSE_FINAL_INCLUDE_ARGPARSE_H

#include "runtime/cpp/native/core/py_runtime.h"

#include "generated/std/sys.h"
#include "runtime/cpp/native/core/exceptions.h"

namespace pytra_mod_argparse {

struct Namespace;
struct _ArgSpec;
struct ArgumentParser;

    struct Namespace {
        dict<str, ::std::variant<str, bool, ::std::monostate>> values;
        
        Namespace(const ::std::optional<dict<str, ::std::variant<str, bool, ::std::monostate>>>& values = ::std::nullopt) {
            if (!values.has_value()) {
                this->values = dict<str, ::std::variant<str, bool, ::std::monostate>>{};
                return;
            }
            this->values = values.value();
        }
    };

    struct _ArgSpec {
        rc<list<str>> names;
        str action;
        rc<list<str>> choices;
        ::std::variant<str, bool, ::std::monostate> py_default;
        str help_text;
        bool is_optional;
        str dest;
        
        _ArgSpec(const rc<list<str>>& names, const str& action = "", const rc<list<str>>& choices = rc_list_from_value(list<str>{}), const ::std::variant<str, bool, ::std::monostate>& py_default = ::std::monostate{}, const str& help_text = "") {
            this->names = names;
            this->action = action;
            this->choices = choices;
            this->py_default = py_default;
            this->help_text = help_text;
            this->is_optional = ((rc_list_ref(names)).size() > 0) && (py_startswith(py_list_at_ref(rc_list_ref(names), 0), "-"));
            if (this->is_optional) {
                auto base = py_replace(py_list_at_ref(rc_list_ref(names), -(1)).lstrip("-"), "-", "_");
                this->dest = py_to_string(base);
            } else {
                this->dest = py_list_at_ref(rc_list_ref(names), 0);
            }
        }
    };

    struct ArgumentParser {
        str description;
        rc<list<_ArgSpec>> _specs;
        
        ArgumentParser(const str& description = "") {
            this->description = description;
            this->_specs = rc_list_from_value(list<_ArgSpec>{});
        }
        void add_argument(const str& name0, const str& name1 = "", const str& name2 = "", const str& name3 = "", const str& help = "", const str& action = "", const rc<list<str>>& choices = rc_list_from_value(list<str>{}), const ::std::variant<str, bool, ::std::monostate>& py_default = ::std::monostate{}) {
            rc<list<str>> names = rc_list_from_value(list<str>{});
            if (name0 != "")
                rc_list_ref(names).append(name0);
            if (name1 != "")
                rc_list_ref(names).append(name1);
            if (name2 != "")
                rc_list_ref(names).append(name2);
            if (name3 != "")
                rc_list_ref(names).append(name3);
            if ((rc_list_ref(names)).empty())
                throw ValueError("add_argument requires at least one name");
            _ArgSpec spec = _ArgSpec(names, action, choices, py_default, help);
            rc_list_ref(this->_specs).append(spec);
        }
        void _fail(const str& msg) const {
            if (msg != "")
                pytra::std::sys::write_stderr("error: " + msg + "\n");
            throw SystemExit(2);
        }
        dict<str, ::std::variant<str, bool, ::std::monostate>> parse_args(const ::std::optional<rc<list<str>>>& argv = ::std::nullopt) const {
            rc<list<str>> args;
            if (!argv.has_value())
                args = py_to<rc<list<str>>>(py_list_slice_copy(py_runtime_argv(), 1, static_cast<int64>((py_runtime_argv()).size())));
            else
                args = py_to<rc<list<str>>>(argv.value());
            rc<list<_ArgSpec>> specs_pos = rc_list_from_value(list<_ArgSpec>{});
            rc<list<_ArgSpec>> specs_opt = rc_list_from_value(list<_ArgSpec>{});
            for (_ArgSpec s : rc_list_ref(this->_specs)) {
                if (s.is_optional)
                    rc_list_ref(specs_opt).append(s);
                else
                    rc_list_ref(specs_pos).append(s);
            }
            dict<str, int64> by_name = {};
            int64 spec_i = 0;
            for (_ArgSpec s : rc_list_ref(specs_opt)) {
                for (str n : rc_list_ref(s.names)) {
                    by_name[n] = spec_i;
                }
                spec_i++;
            }
            dict<str, ::std::variant<str, bool, ::std::monostate>> values = dict<str, ::std::variant<str, bool, ::std::monostate>>{};
            for (_ArgSpec s : rc_list_ref(this->_specs)) {
                if (s.action == "store_true") {
                    values[s.dest] = (!::std::holds_alternative<::std::monostate>(s.py_default) ? py_variant_to_bool(s.py_default) : false);
                } else if (!::std::holds_alternative<::std::monostate>(s.py_default)) {
                    values[s.dest] = s.py_default;
                } else {
                    values[s.dest] = ::std::monostate{};
                }
            }
            int64 pos_i = 0;
            int64 i = 0;
            while (i < (rc_list_ref(args)).size()) {
                str tok = py_list_at_ref(rc_list_ref(args), i);
                if (py_startswith(tok, "-")) {
                    if (!py_contains(by_name, tok))
                        this->_fail("unknown option: " + tok);
                    auto __idx_1 = ([&]() { auto&& __dict_2 = by_name; auto __dict_key_3 = tok; return __dict_2.at(__dict_key_3); }());
                    _ArgSpec spec = py_list_at_ref(rc_list_ref(specs_opt), __idx_1);
                    if (spec.action == "store_true") {
                        values[spec.dest] = true;
                        i++;
                        continue;
                    }
                    if (i + 1 >= (rc_list_ref(args)).size())
                        this->_fail("missing value for option: " + tok);
                    str val = py_list_at_ref(rc_list_ref(args), i + 1);
                    if (((rc_list_ref(spec.choices)).size() > 0) && (!py_contains(spec.choices, val)))
                        this->_fail("invalid choice for " + tok + ": " + val);
                    values[spec.dest] = val;
                    i += 2;
                    continue;
                }
                if (pos_i >= (rc_list_ref(specs_pos)).size())
                    this->_fail("unexpected extra argument: " + tok);
                _ArgSpec spec = py_list_at_ref(rc_list_ref(specs_pos), pos_i);
                values[spec.dest] = tok;
                pos_i++;
                i++;
            }
            if (pos_i < (rc_list_ref(specs_pos)).size())
                this->_fail("missing required argument: " + py_list_at_ref(rc_list_ref(specs_pos), pos_i).dest);
            return values;
        }
    };


}  // namespace pytra_mod_argparse

#endif  // PYTRA__TMP_ARGPARSE_FINAL_INCLUDE_ARGPARSE_H
