// Generated std/time.scala delegates host bindings through this native seam.
// source: src/runtime/cs/std/time_native.cs (reference)

object time_native {
    def perf_counter(): Double = System.nanoTime().toDouble / 1_000_000_000.0
}
