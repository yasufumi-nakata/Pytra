// Generated std/time.go delegates host bindings through this native seam.

package main

import "time"

var time_native_start = time.Now()

func time_native_perf_counter() float64 {
	return float64(time.Since(time_native_start).Nanoseconds()) / 1e9
}
