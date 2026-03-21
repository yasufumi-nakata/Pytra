// Generated std/time.kt delegates host bindings through this native seam.

private val time_native_start = System.nanoTime()

fun time_native_perf_counter(): Double {
    return (System.nanoTime() - time_native_start).toDouble() / 1_000_000_000.0
}
