// std/time_native.dart — hand-written native implementation for pytra.std.time
// source: src/runtime/dart/std/time_native.dart

double perf_counter() =>
    DateTime.now().microsecondsSinceEpoch / 1000000.0;
