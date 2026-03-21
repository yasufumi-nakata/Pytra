// Generated std/time delegates host bindings through this native seam.

#if canImport(Darwin)
import Foundation
private let __pytra_time_start = CFAbsoluteTimeGetCurrent()
func __pytra_time_perf_counter() -> Double {
    return CFAbsoluteTimeGetCurrent() - __pytra_time_start
}
#else
import Glibc
private func __pytra_clock_nsec() -> UInt64 {
    var ts = timespec()
    clock_gettime(CLOCK_MONOTONIC, &ts)
    return UInt64(ts.tv_sec) &* 1_000_000_000 &+ UInt64(ts.tv_nsec)
}
private let __pytra_time_start: UInt64 = __pytra_clock_nsec()
func __pytra_time_perf_counter() -> Double {
    return Double(__pytra_clock_nsec() &- __pytra_time_start) / 1_000_000_000.0
}
#endif
