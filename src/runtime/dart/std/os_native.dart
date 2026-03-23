// std/os_native.dart — stub native for pytra.std.os
// source: src/runtime/dart/std/os_native.dart

import 'dart:io';

String getcwd() => Directory.current.path;

void mkdir(dynamic path, [dynamic existOk]) {
  bool eo = (existOk == true);
  try {
    Directory(path.toString()).createSync(recursive: false);
  } catch (e) {
    if (!eo) rethrow;
  }
}

void makedirs(dynamic path, [dynamic existOk]) {
  bool eo = (existOk == true);
  try {
    Directory(path.toString()).createSync(recursive: true);
  } catch (e) {
    if (!eo) rethrow;
  }
}
