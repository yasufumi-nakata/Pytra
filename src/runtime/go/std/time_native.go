// time_native.go: @extern delegation for pytra.std.time.
// Hand-written native implementation.
package main

import "time"

var _pytra_perf_counter_start = time.Now()

func perf_counter() float64 {
	return float64(time.Since(_pytra_perf_counter_start).Nanoseconds()) / 1e9
}
func py_perf_counter() float64 { return perf_counter() }
