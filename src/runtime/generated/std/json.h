// AUTO-GENERATED FILE. DO NOT EDIT.
// source: /workspace/Pytra/src/runtime/generated/std/json.east
// generated-by: src/toolchain/emit/cpp/cli.py

#ifndef PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_JSON_H
#define PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_JSON_H

#include "runtime/cpp/core/py_runtime.h"

#include <tuple>
#include <optional>
#include "runtime/cpp/core/exceptions.h"

namespace pytra::std::json {

struct JsonObj;
struct JsonArr;
struct JsonValue;
struct _JsonParser;

struct JsonVal {
    pytra_type_id tag;
    bool bool_val;
    int64 int64_val;
    float64 float64_val;
    str str_val;
    rc<list<JsonVal>> list_jsonval_val;
    rc<dict<str, JsonVal>> dict_str_jsonval_val;

    JsonVal() : tag(PYTRA_TID_NONE) {}
    JsonVal(const bool& v) : tag(PYTRA_TID_BOOL), bool_val(v) {}
    JsonVal(const int64& v) : tag(PYTRA_TID_INT), int64_val(v) {}
    JsonVal(const float64& v) : tag(PYTRA_TID_FLOAT), float64_val(v) {}
    JsonVal(const str& v) : tag(PYTRA_TID_STR), str_val(v) {}
    JsonVal(const rc<list<JsonVal>>& v) : tag(PYTRA_TID_LIST), list_jsonval_val(v) {}
    JsonVal(const rc<dict<str, JsonVal>>& v) : tag(PYTRA_TID_DICT), dict_str_jsonval_val(v) {}
    JsonVal(::std::monostate) : tag(PYTRA_TID_NONE) {}
};


extern str _EMPTY;
extern str _COMMA_NL;
extern str _HEX_DIGITS;

    struct JsonObj {
        dict<str, JsonVal> raw;
        
        JsonObj(const dict<str, JsonVal>& raw) {
            this->raw = raw;
        }
        ::std::optional<JsonValue> get(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key));
        }
        ::std::optional<JsonObj> get_obj(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key)).as_obj();
        }
        ::std::optional<JsonArr> get_arr(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key)).as_arr();
        }
        ::std::optional<str> get_str(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key)).as_str();
        }
        ::std::optional<int64> get_int(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key)).as_int();
        }
        ::std::optional<float64> get_float(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key)).as_float();
        }
        ::std::optional<bool> get_bool(const str& key) const {
            if (!py_contains(this->raw, key))
                return ::std::nullopt;
            return JsonValue(_jv_obj_require(this->raw, key)).as_bool();
        }
    };

    struct JsonArr {
        Object<list<JsonVal>> raw;
        
        JsonArr(const Object<list<JsonVal>>& raw) {
            this->raw = raw;
        }
        ::std::optional<JsonValue> get(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index));
        }
        ::std::optional<JsonObj> get_obj(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index)).as_obj();
        }
        ::std::optional<JsonArr> get_arr(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index)).as_arr();
        }
        ::std::optional<str> get_str(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index)).as_str();
        }
        ::std::optional<int64> get_int(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index)).as_int();
        }
        ::std::optional<float64> get_float(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index)).as_float();
        }
        ::std::optional<bool> get_bool(int64 index) const {
            if ((index < 0) || (index >= (rc_list_ref(this->raw)).size()))
                return ::std::nullopt;
            return JsonValue(py_list_at_ref(rc_list_ref(this->raw), index)).as_bool();
        }
    };

    struct JsonValue {
        JsonVal raw;
        
        JsonValue(const JsonVal& raw) {
            this->raw = raw;
        }
        ::std::optional<JsonObj> as_obj() const {
            JsonVal jv = this->raw;
            if ((jv).tag == PYTRA_TID_DICT)
                return JsonObj(jv.as<dict>());
            return ::std::nullopt;
        }
        ::std::optional<JsonArr> as_arr() const {
            JsonVal jv = this->raw;
            if ((jv).tag == PYTRA_TID_LIST)
                return JsonArr(py_to<Object<list<JsonVal>>>(jv.as<list>()));
            return ::std::nullopt;
        }
        ::std::optional<str> as_str() const {
            JsonVal jv = this->raw;
            if ((jv).tag == PYTRA_TID_STR)
                return jv.unbox<str, PYTRA_TID_STR>();
            return ::std::nullopt;
        }
        ::std::optional<int64> as_int() const {
            JsonVal jv = this->raw;
            if ((jv).tag == PYTRA_TID_INT)
                return jv.unbox<int64, PYTRA_TID_INT>();
            return ::std::nullopt;
        }
        ::std::optional<float64> as_float() const {
            JsonVal jv = this->raw;
            if ((jv).tag == PYTRA_TID_FLOAT)
                return jv.unbox<float64, PYTRA_TID_FLOAT>();
            return ::std::nullopt;
        }
        ::std::optional<bool> as_bool() const {
            JsonVal jv = this->raw;
            if ((jv).tag == PYTRA_TID_BOOL)
                return jv.unbox<bool, PYTRA_TID_BOOL>();
            return ::std::nullopt;
        }
    };

    struct _JsonParser {
        str text;
        int64 n;
        int64 i;
        
        _JsonParser(const str& text) {
            this->text = text;
            this->n = text.size();
            this->i = 0;
        }
        JsonVal parse() {
            this->_skip_ws();
            JsonVal out = this->_parse_value();
            this->_skip_ws();
            if (this->i != this->n)
                throw ValueError("invalid json: trailing characters");
            return out;
        }
        void _skip_ws() {
            while ((this->i < this->n) && (_is_ws(this->text[this->i]))) {
                this->i++;
            }
        }
        JsonVal _parse_value() {
            if (this->i >= this->n)
                throw ValueError("invalid json: unexpected end");
            str ch = this->text[this->i];
            if (ch == "{")
                return this->_parse_object();
            if (ch == "[")
                return this->_parse_array();
            if (ch == "\"")
                return this->_parse_string();
            if ((ch == "t") && (py_str_slice(this->text, this->i, this->i + 4) == "true")) {
                this->i += 4;
                return true;
            }
            if ((ch == "f") && (py_str_slice(this->text, this->i, this->i + 5) == "false")) {
                this->i += 5;
                return false;
            }
            if ((ch == "n") && (py_str_slice(this->text, this->i, this->i + 4) == "null")) {
                this->i += 4;
                return ::std::nullopt;
            }
            return this->_parse_number();
        }
        dict<str, JsonVal> _parse_object() {
            dict<str, JsonVal> out = {};
            this->i++;
            this->_skip_ws();
            if ((this->i < this->n) && (this->text[this->i] == "}")) {
                this->i++;
                return out;
            }
            while (true) {
                this->_skip_ws();
                if ((this->i >= this->n) || (this->text[this->i] != "\""))
                    throw ValueError("invalid json object key");
                str key = this->_parse_string();
                this->_skip_ws();
                if ((this->i >= this->n) || (this->text[this->i] != ":"))
                    throw ValueError("invalid json object: missing ':'");
                this->i++;
                this->_skip_ws();
                out[key] = this->_parse_value();
                this->_skip_ws();
                if (this->i >= this->n)
                    throw ValueError("invalid json object: unexpected end");
                str ch = this->text[this->i];
                this->i++;
                if (ch == "}")
                    return out;
                if (ch != ",")
                    throw ValueError("invalid json object separator");
            }
        }
        Object<list<JsonVal>> _parse_array() {
            Object<list<JsonVal>> out = rc_list_from_value(list<JsonVal>{});
            this->i++;
            this->_skip_ws();
            if ((this->i < this->n) && (this->text[this->i] == "]")) {
                this->i++;
                return out;
            }
            while (true) {
                this->_skip_ws();
                rc_list_ref(out).append(this->_parse_value());
                this->_skip_ws();
                if (this->i >= this->n)
                    throw ValueError("invalid json array: unexpected end");
                str ch = this->text[this->i];
                this->i++;
                if (ch == "]")
                    return out;
                if (ch != ",")
                    throw ValueError("invalid json array separator");
            }
        }
        str _parse_string() {
            if (this->text[this->i] != "\"")
                throw ValueError("invalid json string");
            this->i++;
            Object<list<str>> out_chars = rc_list_from_value(list<str>{});
            while (this->i < this->n) {
                str ch = this->text[this->i];
                this->i++;
                if (ch == "\"")
                    return _join_strs(out_chars, _EMPTY);
                if (ch == "\\") {
                    if (this->i >= this->n)
                        throw ValueError("invalid json string escape");
                    str esc = this->text[this->i];
                    this->i++;
                    if (esc == "\"") {
                        rc_list_ref(out_chars).append("\"");
                    } else if (esc == "\\") {
                        rc_list_ref(out_chars).append("\\");
                    } else if (esc == "/") {
                        rc_list_ref(out_chars).append("/");
                    } else if (esc == "b") {
                        rc_list_ref(out_chars).append("\b");
                    } else if (esc == "f") {
                        rc_list_ref(out_chars).append("\f");
                    } else if (esc == "n") {
                        rc_list_ref(out_chars).append("\n");
                    } else if (esc == "r") {
                        rc_list_ref(out_chars).append("\r");
                    } else if (esc == "t") {
                        rc_list_ref(out_chars).append("\t");
                    } else if (esc == "u") {
                        if (this->i + 4 > this->n)
                            throw ValueError("invalid json unicode escape");
                        str hx = py_str_slice(this->text, this->i, this->i + 4);
                        this->i += 4;
                        rc_list_ref(out_chars).append(py_chr(_int_from_hex4(hx)));
                    } else {
                        throw ValueError("invalid json escape");
                    }
                } else {
                    rc_list_ref(out_chars).append(ch);
                }
            }
            throw ValueError("unterminated json string");
        }
        JsonVal _parse_number() {
            int64 start = this->i;
            if (this->text[this->i] == "-")
                this->i++;
            if (this->i >= this->n)
                throw ValueError("invalid json number");
            if (this->text[this->i] == "0") {
                this->i++;
            } else {
                if (!(_is_digit(this->text[this->i])))
                    throw ValueError("invalid json number");
                while ((this->i < this->n) && (_is_digit(this->text[this->i]))) {
                    this->i++;
                }
            }
            bool is_float = false;
            if ((this->i < this->n) && (this->text[this->i] == ".")) {
                is_float = true;
                this->i++;
                if ((this->i >= this->n) || (!(_is_digit(this->text[this->i]))))
                    throw ValueError("invalid json number");
                while ((this->i < this->n) && (_is_digit(this->text[this->i]))) {
                    this->i++;
                }
            }
            if (this->i < this->n) {
                str exp_ch = this->text[this->i];
                if ((exp_ch == "e") || (exp_ch == "E")) {
                    is_float = true;
                    this->i++;
                    if (this->i < this->n) {
                        str sign = this->text[this->i];
                        if ((sign == "+") || (sign == "-"))
                            this->i++;
                    }
                    if ((this->i >= this->n) || (!(_is_digit(this->text[this->i]))))
                        throw ValueError("invalid json exponent");
                    while ((this->i < this->n) && (_is_digit(this->text[this->i]))) {
                        this->i++;
                    }
                }
            }
            str token = py_str_slice(this->text, start, this->i);
            if (is_float) {
                float64 num_f = float64(::std::stod(token.std()));
                return num_f;
            }
            int64 num_i = int64(::std::stoll(token));
            return num_i;
        }
    };


bool _is_ws(const str& ch);
bool _is_digit(const str& ch);
int64 _hex_value(const str& ch);
int64 _int_from_hex4(const str& hx);
str _hex4(int64 code);
int64 _json_indent_value(const ::std::optional<int64>& indent);
JsonVal _jv_obj_require(const dict<str, JsonVal>& raw, const str& key);
JsonValue loads(const str& text);
::std::optional<JsonObj> loads_obj(const str& text);
::std::optional<JsonArr> loads_arr(const str& text);
str _join_strs(const rc<list<str>>& parts, const str& sep);
str _escape_str(const str& s, bool ensure_ascii);
str _dump_json_list(const rc<list<JsonVal>>& values, bool ensure_ascii, const ::std::optional<int64>& indent, const str& item_sep, const str& key_sep, int64 level);
str _dump_json_dict(const dict<str, JsonVal>& values, bool ensure_ascii, const ::std::optional<int64>& indent, const str& item_sep, const str& key_sep, int64 level);
str _dump_json_value(const JsonVal& v, bool ensure_ascii, const ::std::optional<int64>& indent, const str& item_sep, const str& key_sep, int64 level);
str dumps(const JsonVal& obj, bool ensure_ascii = true, const ::std::optional<int64>& indent = ::std::nullopt, const ::std::optional<::std::tuple<str, str>>& separators = ::std::nullopt);
str dumps_jv(const JsonVal& jv, bool ensure_ascii = true, const ::std::optional<int64>& indent = ::std::nullopt, const ::std::optional<::std::tuple<str, str>>& separators = ::std::nullopt);

}  // namespace pytra::std::json

using namespace pytra::std::json;
#endif  // PYTRA__WORKSPACE_PYTRA_SRC_RUNTIME_GENERATED_STD_JSON_H
