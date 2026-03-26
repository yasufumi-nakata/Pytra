// py_runtime.go: Python built-in function equivalents.
// Only contains Python built-in functions. pytra.std.* and pytra.utils.* are
// provided by native files (std/) or pipeline-generated code (utils/).
// See docs/ja/spec/spec-emitter-guide.md §6.
package main

import (
	"fmt"
	"io"
	"os"
	"reflect"
	"strconv"
	"strings"
)

func py_print(args ...any) {
	parts := make([]string, len(args))
	for i, a := range args {
		parts[i] = py_str(a)
	}
	fmt.Println(strings.Join(parts, " "))
}

func py_str(v any) string {
	if v == nil {
		return "None"
	}
	rv := reflect.ValueOf(v)
	for rv.IsValid() && (rv.Kind() == reflect.Interface || rv.Kind() == reflect.Pointer) {
		if rv.IsNil() {
			return "None"
		}
		rv = rv.Elem()
		v = rv.Interface()
	}
	switch t := v.(type) {
	case bool:
		if t {
			return "True"
		}
		return "False"
	}
	return fmt.Sprint(v)
}
func py_to_string(v any) string { return py_str(v) }

type PyFile struct {
	file *os.File
}

func py_open(path string, mode string, _kwargs ...any) *PyFile {
	var flag int
	switch mode {
	case "r":
		flag = os.O_RDONLY
	case "w":
		flag = os.O_WRONLY | os.O_CREATE | os.O_TRUNC
	default:
		panic("unsupported open mode: " + mode)
	}
	f, err := os.OpenFile(path, flag, 0644)
	if err != nil {
		panic(err)
	}
	return &PyFile{file: f}
}

func (f *PyFile) read() string {
	data, err := io.ReadAll(f.file)
	if err != nil {
		panic(err)
	}
	return string(data)
}

func (f *PyFile) write(text string) int64 {
	n, err := f.file.WriteString(text)
	if err != nil {
		panic(err)
	}
	return int64(n)
}

func (f *PyFile) close() {
	if err := f.file.Close(); err != nil {
		panic(err)
	}
}

func py_len(v any) int64 {
	switch t := v.(type) {
	case string:
		return int64(len(t))
	case []int64:
		return int64(len(t))
	case []float64:
		return int64(len(t))
	case []string:
		return int64(len(t))
	case []byte:
		return int64(len(t))
	case []any:
		return int64(len(t))
	default:
		return 0
	}
}

func py_abs(v int64) int64 {
	if v < 0 {
		return -v
	}
	return v
}
func py_abs_float(v float64) float64 {
	if v < 0 {
		return -v
	}
	return v
}
func py_min_int(a, b int64) int64 {
	if a < b {
		return a
	}
	return b
}
func py_max_int(a, b int64) int64 {
	if a > b {
		return a
	}
	return b
}
func py_min_float(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
func py_max_float(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}

func py_floordiv(a, b int64) int64 {
	q := a / b
	if (a^b) < 0 && q*b != a {
		q -= 1
	}
	return q
}

func py_truthy(v any) bool {
	if v == nil {
		return false
	}
	rv := reflect.ValueOf(v)
	switch rv.Kind() {
	case reflect.Bool:
		return rv.Bool()
	case reflect.String, reflect.Array, reflect.Slice, reflect.Map:
		return rv.Len() != 0
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return rv.Int() != 0
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return rv.Uint() != 0
	case reflect.Float32, reflect.Float64:
		return rv.Float() != 0
	case reflect.Interface, reflect.Pointer:
		return !rv.IsNil()
	default:
		return true
	}
}

func py_bool(v any) bool { return py_truthy(v) }

func py_eq(a any, b any) bool {
	if reflect.DeepEqual(a, b) {
		return true
	}
	av := reflect.ValueOf(a)
	bv := reflect.ValueOf(b)
	if !av.IsValid() || !bv.IsValid() {
		return !av.IsValid() && !bv.IsValid()
	}
	if av.Type().ConvertibleTo(bv.Type()) {
		return reflect.DeepEqual(av.Convert(bv.Type()).Interface(), b)
	}
	if bv.Type().ConvertibleTo(av.Type()) {
		return reflect.DeepEqual(a, bv.Convert(av.Type()).Interface())
	}
	return false
}

func py_contains(haystack any, needle any) bool {
	switch h := haystack.(type) {
	case string:
		switch n := needle.(type) {
		case string:
			return strings.Contains(h, n)
		case byte:
			return strings.Contains(h, string([]byte{n}))
		}
	}
	rv := reflect.ValueOf(haystack)
	if !rv.IsValid() {
		return false
	}
	switch rv.Kind() {
	case reflect.Array, reflect.Slice:
		for i := 0; i < rv.Len(); i++ {
			if py_eq(rv.Index(i).Interface(), needle) {
				return true
			}
		}
	case reflect.Map:
		kv := reflect.ValueOf(needle)
		if !kv.IsValid() {
			return false
		}
		if kv.Type().AssignableTo(rv.Type().Key()) {
			return rv.MapIndex(kv).IsValid()
		}
		if kv.Type().ConvertibleTo(rv.Type().Key()) {
			return rv.MapIndex(kv.Convert(rv.Type().Key())).IsValid()
		}
	}
	return false
}

func py_is_none(v any) bool {
	if v == nil {
		return true
	}
	rv := reflect.ValueOf(v)
	if !rv.IsValid() {
		return true
	}
	if rv.Kind() == reflect.Interface || rv.Kind() == reflect.Pointer {
		return rv.IsNil()
	}
	return false
}

func py_is_bool_type(v any) bool {
	rv := reflect.ValueOf(v)
	return rv.IsValid() && rv.Kind() == reflect.Bool
}

func py_is_int(v any) bool {
	rv := reflect.ValueOf(v)
	if !rv.IsValid() {
		return false
	}
	switch rv.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return true
	default:
		return false
	}
}

func py_is_str(v any) bool {
	rv := reflect.ValueOf(v)
	return rv.IsValid() && rv.Kind() == reflect.String
}

func py_is_list(v any) bool {
	rv := reflect.ValueOf(v)
	if !rv.IsValid() {
		return false
	}
	return rv.Kind() == reflect.Slice || rv.Kind() == reflect.Array
}

func py_is_dict(v any) bool {
	rv := reflect.ValueOf(v)
	return rv.IsValid() && rv.Kind() == reflect.Map
}

func py_ternary_int(cond bool, a, b int64) int64 {
	if cond {
		return a
	}
	return b
}
func py_ternary_float(cond bool, a, b float64) float64 {
	if cond {
		return a
	}
	return b
}
func py_ternary_str(cond bool, a, b string) string {
	if cond {
		return a
	}
	return b
}
func py_append_byte(s []byte, v any) []byte {
	switch t := v.(type) {
	case byte:
		return append(s, t)
	case int64:
		return append(s, byte(t))
	case int:
		return append(s, byte(t))
	default:
		return s
	}
}

func py_list_pop(seq any, args ...int64) any {
	rv := reflect.ValueOf(seq)
	if !rv.IsValid() || rv.Kind() != reflect.Pointer {
		panic("py_list_pop expects pointer to slice")
	}
	sv := rv.Elem()
	if sv.Kind() != reflect.Slice {
		panic("py_list_pop expects pointer to slice")
	}
	n := sv.Len()
	idx := n - 1
	if len(args) > 0 {
		idx = int(args[0])
		if idx < 0 {
			idx += n
		}
	}
	if idx < 0 || idx >= n {
		panic("pop index out of range")
	}
	val := sv.Index(idx).Interface()
	newSlice := reflect.AppendSlice(sv.Slice(0, idx), sv.Slice(idx+1, n))
	sv.Set(newSlice)
	return val
}

func py_repeat_int64(val, count int64) []int64 {
	s := make([]int64, count)
	for i := int64(0); i < count; i++ {
		s[i] = val
	}
	return s
}

// String methods
func py_str_isdigit(v any) bool {
	switch t := v.(type) {
	case byte:
		return t >= '0' && t <= '9'
	case string:
		if len(t) == 0 {
			return false
		}
		for _, c := range t {
			if c < '0' || c > '9' {
				return false
			}
		}
		return true
	}
	return false
}
func py_str_isalpha(v any) bool {
	switch t := v.(type) {
	case byte:
		return (t >= 'a' && t <= 'z') || (t >= 'A' && t <= 'Z')
	case string:
		if len(t) == 0 {
			return false
		}
		for _, c := range t {
			if !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
				return false
			}
		}
		return true
	}
	return false
}
func py_str_strip(s string) string                  { return strings.TrimSpace(s) }
func py_str_join(sep string, items []string) string { return strings.Join(items, sep) }
func py_str_replace(s, old, new_ string) string     { return strings.ReplaceAll(s, old, new_) }
func py_str_split(s, sep string) []string           { return strings.Split(s, sep) }
func py_str_startswith(s, prefix string) bool       { return strings.HasPrefix(s, prefix) }
func py_str_endswith(s, suffix string) bool         { return strings.HasSuffix(s, suffix) }
func py_str_upper(s string) string                  { return strings.ToUpper(s) }
func py_str_lower(s string) string                  { return strings.ToLower(s) }
func py_str_find(s, sub string) int64               { return int64(strings.Index(s, sub)) }

// Dict
func py_dict_get(m any, key any, def_ any) any {
	mv := reflect.ValueOf(m)
	if !mv.IsValid() || mv.Kind() != reflect.Map {
		return def_
	}
	kv := reflect.ValueOf(key)
	if !kv.IsValid() {
		return def_
	}
	if kv.Type().AssignableTo(mv.Type().Key()) {
		v := mv.MapIndex(kv)
		if v.IsValid() {
			return v.Interface()
		}
		return def_
	}
	if kv.Type().ConvertibleTo(mv.Type().Key()) {
		v := mv.MapIndex(kv.Convert(mv.Type().Key()))
		if v.IsValid() {
			return v.Interface()
		}
	}
	return def_
}

func py_items(m any) [][]any {
	mv := reflect.ValueOf(m)
	if !mv.IsValid() || mv.Kind() != reflect.Map {
		return [][]any{}
	}
	keys := mv.MapKeys()
	out := make([][]any, 0, len(keys))
	for _, key := range keys {
		value := mv.MapIndex(key)
		out = append(out, []any{key.Interface(), value.Interface()})
	}
	return out
}

func py_to_map_string_any(v any) map[string]any {
	if v == nil {
		return nil
	}
	if m, ok := v.(map[string]any); ok {
		return m
	}
	mv := reflect.ValueOf(v)
	if !mv.IsValid() || mv.Kind() != reflect.Map || mv.Type().Key().Kind() != reflect.String {
		panic("py_to_map_string_any: expected map with string keys")
	}
	out := map[string]any{}
	iter := mv.MapRange()
	for iter.Next() {
		out[iter.Key().String()] = iter.Value().Interface()
	}
	return out
}

// Type conversions
func py_byte_eq(b byte, s string) bool   { return len(s) == 1 && b == s[0] }
func py_byte_to_string(b byte) string    { return string([]byte{b}) }
func py_str_to_int64(s string) int64     { v, _ := strconv.ParseInt(s, 10, 64); return v }
func py_str_to_float64(s string) float64 { v, _ := strconv.ParseFloat(s, 64); return v }

func _toF64(v any) float64 {
	switch t := v.(type) {
	case float64:
		return t
	case int64:
		return float64(t)
	case int:
		return float64(t)
	case float32:
		return float64(t)
	default:
		return 0
	}
}
func py_to_int64(v any) int64 {
	switch t := v.(type) {
	case int64:
		return t
	case int:
		return int64(t)
	case float64:
		return int64(t)
	default:
		return 0
	}
}
func py_to_float64(v any) float64 { return _toF64(v) }
func py_int64(v any) int64 {
	switch t := v.(type) {
	case int:
		return int64(t)
	case int64:
		return t
	case float64:
		return int64(t)
	case string:
		r, _ := strconv.ParseInt(t, 10, 64)
		return r
	}
	return 0
}
