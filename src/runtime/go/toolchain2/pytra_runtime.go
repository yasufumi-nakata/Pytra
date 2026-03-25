// pytra_runtime.go: toolchain2 Go emitter 用ランタイム。
//
// toolchain2/emit/go/ が生成するコードが呼び出す関数を提供する。
// 関数名は EAST3 の import 名 / runtime_call 名に一致させる。
//
// source: src/runtime/go/toolchain2/pytra_runtime.go

package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// ---------------------------------------------------------------------------
// print / str
// ---------------------------------------------------------------------------

// __pytra_print emulates Python's print(): space-separated args + newline.
func __pytra_print(args ...interface{}) {
	parts := make([]string, len(args))
	for i, a := range args {
		parts[i] = fmt.Sprint(a)
	}
	fmt.Println(strings.Join(parts, " "))
}

// __pytra_str converts any value to string (Python str()).
func __pytra_str(v interface{}) string {
	return fmt.Sprint(v)
}

// ---------------------------------------------------------------------------
// time
// ---------------------------------------------------------------------------

var _pytra_perf_counter_start = time.Now()

// perf_counter returns seconds since an arbitrary epoch (Python time.perf_counter).
func perf_counter() float64 {
	return float64(time.Since(_pytra_perf_counter_start).Nanoseconds()) / 1e9
}

// ---------------------------------------------------------------------------
// pathlib
// ---------------------------------------------------------------------------

// Path is a minimal pathlib.Path equivalent.
func Path(s string) string {
	return s
}

// __pytra_write_text writes content to a file (Python Path.write_text).
func __pytra_write_text(path string, content string) {
	dir := filepath.Dir(path)
	if dir != "" && dir != "." {
		os.MkdirAll(dir, 0755)
	}
	os.WriteFile(path, []byte(content), 0644)
}

// ---------------------------------------------------------------------------
// numeric / container helpers
// ---------------------------------------------------------------------------

// __pytra_len returns the length of a slice or string.
func __pytra_len(v interface{}) int64 {
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
	case []interface{}:
		return int64(len(t))
	default:
		return 0
	}
}

// __pytra_abs returns the absolute value.
func __pytra_abs(v int64) int64 {
	if v < 0 {
		return -v
	}
	return v
}

// __pytra_abs_float returns the absolute value of a float.
func __pytra_abs_float(v float64) float64 {
	if v < 0 {
		return -v
	}
	return v
}

// __pytra_min returns the minimum of two int64 values.
func __pytra_min(a int64, b int64) int64 {
	if a < b {
		return a
	}
	return b
}

// __pytra_max returns the maximum of two int64 values.
func __pytra_max(a int64, b int64) int64 {
	if a > b {
		return a
	}
	return b
}

// __pytra_floordiv performs Python-style floor division.
func __pytra_floordiv(a int64, b int64) int64 {
	q := a / b
	if (a^b) < 0 && q*b != a {
		q -= 1
	}
	return q
}

// __pytra_contains checks if needle is in haystack (Python `in` operator).
func __pytra_contains(haystack interface{}, needle interface{}) bool {
	switch h := haystack.(type) {
	case string:
		n, ok := needle.(string)
		if ok {
			return strings.Contains(h, n)
		}
	case []int64:
		n, ok := needle.(int64)
		if ok {
			for _, v := range h {
				if v == n {
					return true
				}
			}
		}
	case map[string]int64:
		n, ok := needle.(string)
		if ok {
			_, exists := h[n]
			return exists
		}
	}
	return false
}

// ---------------------------------------------------------------------------
// string methods
// ---------------------------------------------------------------------------

// __pytra_isdigit checks if a byte/string is a digit character.
func __pytra_isdigit(v interface{}) bool {
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

// __pytra_isalpha checks if a byte/string is alphabetic.
func __pytra_isalpha(v interface{}) bool {
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

// __pytra_strip removes leading/trailing whitespace.
func __pytra_strip(s string) string {
	return strings.TrimSpace(s)
}

// __pytra_join joins strings with separator (Python str.join).
func __pytra_join(sep string, items []string) string {
	return strings.Join(items, sep)
}

// __pytra_replace replaces occurrences in a string.
func __pytra_replace(s string, old string, new_ string) string {
	return strings.ReplaceAll(s, old, new_)
}

// __pytra_split splits a string by separator.
func __pytra_split(s string, sep string) []string {
	return strings.Split(s, sep)
}

// __pytra_startswith checks string prefix.
func __pytra_startswith(s string, prefix string) bool {
	return strings.HasPrefix(s, prefix)
}

// __pytra_endswith checks string suffix.
func __pytra_endswith(s string, suffix string) bool {
	return strings.HasSuffix(s, suffix)
}

// __pytra_upper converts string to uppercase.
func __pytra_upper(s string) string {
	return strings.ToUpper(s)
}

// __pytra_lower converts string to lowercase.
func __pytra_lower(s string) string {
	return strings.ToLower(s)
}

// __pytra_find finds substring index (-1 if not found).
func __pytra_find(s string, sub string) int64 {
	return int64(strings.Index(s, sub))
}

// ---------------------------------------------------------------------------
// dict helpers
// ---------------------------------------------------------------------------

// __pytra_dict_get gets a value from map with default (for map[string]int64).
func __pytra_dict_get(m map[string]int64, key string, def_ int64) int64 {
	if v, ok := m[key]; ok {
		return v
	}
	return def_
}

// ---------------------------------------------------------------------------
// string/byte helpers
// ---------------------------------------------------------------------------

// __pytra_byte_eq compares a byte to a string character.
func __pytra_byte_eq(b byte, s string) bool {
	return len(s) == 1 && b == s[0]
}

// __pytra_byte_to_string converts a byte to a single-char string.
func __pytra_byte_to_string(b byte) string {
	return string([]byte{b})
}

// __pytra_str_to_int64 converts a string to int64 (Python int(str)).
func __pytra_str_to_int64(s string) int64 {
	v, _ := strconv.ParseInt(s, 10, 64)
	return v
}

// __pytra_int64 converts various types to int64.
func __pytra_int64(v interface{}) int64 {
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
