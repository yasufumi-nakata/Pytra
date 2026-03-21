// Generated std/time delegates host bindings through this native seam.

package main

import "time"

var __pytra_time_start = time.Now()

func __pytra_time_perf_counter() float64 {
	return float64(time.Since(__pytra_time_start).Nanoseconds()) / 1e9
}
