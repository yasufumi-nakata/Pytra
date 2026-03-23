// std/glob_native.dart — stub native for pytra.std.glob
// source: src/runtime/dart/std/glob_native.dart

import 'dart:io';

List<String> glob(String pattern) {
  return Directory('.').listSync(recursive: true)
      .where((e) => e.path.contains(pattern))
      .map((e) => e.path)
      .toList();
}
