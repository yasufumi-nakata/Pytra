// std/os_path_native.dart — stub native for pytra.std.os_path
// source: src/runtime/dart/std/os_path_native.dart

import 'dart:io';

String join(String a, String b) => '$a/$b';
String dirname(String p) {
  int idx = p.lastIndexOf('/');
  return idx < 0 ? '' : p.substring(0, idx);
}
String basename(String p) {
  int idx = p.lastIndexOf('/');
  return idx < 0 ? p : p.substring(idx + 1);
}
List<String> splitext(String p) {
  int idx = p.lastIndexOf('.');
  return idx < 0 ? [p, ''] : [p.substring(0, idx), p.substring(idx)];
}
String abspath(String p) => File(p).absolute.path;
bool exists(String p) => File(p).existsSync() || Directory(p).existsSync();
