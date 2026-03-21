// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/std/re.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_RE_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_RE_H

#include "runtime/cpp/core/py_runtime.h"

#include <optional>
#include "runtime/cpp/core/exceptions.h"

namespace pytra::std::re {

struct Match;

extern int64 S;

    struct Match {
        Object<list<str>> _groups;
        str _text;
        
        Match(const str& text, const Object<list<str>>& groups) {
            this->_text = text;
            this->_groups = groups;
        }
        str group(int64 idx = 0) const {
            if (idx == 0)
                return this->_text;
            if ((idx < 0) || (idx > (rc_list_ref(this->_groups)).size()))
                throw IndexError("group index out of range");
            return py_list_at_ref(rc_list_ref(this->_groups), idx - 1);
        }
    };


str group(const ::std::optional<rc<Match>>& m, int64 idx = 0);
str strip_group(const ::std::optional<rc<Match>>& m, int64 idx = 0);
bool _is_ident(const str& s);
bool _is_dotted_ident(const str& s);
str _strip_suffix_colon(const str& s);
bool _is_space_ch(const str& ch);
bool _is_alnum_or_underscore(const str& ch);
int64 _skip_spaces(const str& t, int64 i);
::std::optional<rc<Match>> match(const str& pattern, const str& text, int64 flags = 0);
str sub(const str& pattern, const str& repl, const str& text, int64 flags = 0);

}  // namespace pytra::std::re

using namespace pytra::std::re;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_RE_H
