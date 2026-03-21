import 'py_runtime.dart';
import 'dart:math' as math;
import 'gif/east.dart';


var perf_counter = pytraPerfCounter;

// --- pytra runtime helpers ---
String __pytraPrintRepr(dynamic v) {
  if (v == true) return 'True';
  if (v == false) return 'False';
  if (v == null) return 'None';
  return v.toString();
}

void __pytraPrint(List<dynamic> args) {
  print(args.map(__pytraPrintRepr).join(' '));
}

bool __pytraTruthy(dynamic v) {
  if (v == null) return false;
  if (v is bool) return v;
  if (v is num) return v != 0;
  if (v is String) return v.isNotEmpty;
  if (v is List) return v.isNotEmpty;
  if (v is Map) return v.isNotEmpty;
  return true;
}

bool __pytraContains(dynamic container, dynamic value) {
  if (container is List) return container.contains(value);
  if (container is Map) return container.containsKey(value);
  if (container is Set) return container.contains(value);
  if (container is String) return container.contains(value.toString());
  return false;
}

dynamic __pytraRepeatSeq(dynamic a, dynamic b) {
  dynamic seq = a;
  dynamic count = b;
  if (a is num && b is! num) { seq = b; count = a; }
  int n = (count is num) ? count.toInt() : 0;
  if (n <= 0) {
    if (seq is String) return '';
    return [];
  }
  if (seq is String) return seq * n;
  if (seq is List) {
    var out = [];
    for (var i = 0; i < n; i++) { out.addAll(seq); }
    return out;
  }
  return (a is num ? a : 0) * (b is num ? b : 0);
}

bool __pytraStrIsdigit(String s) {
  if (s.isEmpty) return false;
  for (var i = 0; i < s.length; i++) {
    var c = s.codeUnitAt(i);
    if (c < 48 || c > 57) return false;
  }
  return true;
}

bool __pytraStrIsalpha(String s) {
  if (s.isEmpty) return false;
  for (var i = 0; i < s.length; i++) {
    var c = s.codeUnitAt(i);
    if (!((c >= 65 && c <= 90) || (c >= 97 && c <= 122))) return false;
  }
  return true;
}

bool __pytraStrIsalnum(String s) {
  if (s.isEmpty) return false;
  for (var i = 0; i < s.length; i++) {
    var c = s.codeUnitAt(i);
    if (!((c >= 48 && c <= 57) || (c >= 65 && c <= 90) || (c >= 97 && c <= 122))) return false;
  }
  return true;
}
// --- end runtime helpers ---

// 10: Sample that outputs a plasma effect as a GIF.

void run_10_plasma_effect() {
  int w = 320;
  int h = 240;
  int frames_n = 216;
  String out_path = "sample/out/10_plasma_effect.gif";
  
  double start = perf_counter();
  var frames = [];
  
  for (var t = 0; t < frames_n; t++) {
    var frame = pytraBytearray((w * h));
    for (var y = 0; y < h; y++) {
      int row_base = (y * w);
      for (var x = 0; x < w; x++) {
        int dx = (x - 160);
        int dy = (y - 120);
        dynamic v = (((math.sin(((x + (t * 2.0)) * 0.045)) + math.sin(((y - (t * 1.2)) * 0.05))) + math.sin((((x + y) + (t * 1.7)) * 0.03))) + math.sin(((math.sqrt(((dx * dx) + (dy * dy))) * 0.07) - (t * 0.18))));
        int c = pytraInt(((v + 4.0) * (255.0 / 8.0)));
        if ((c < 0)) {
          c = 0;
        }
        if ((c > 255)) {
          c = 255;
        }
        frame[(row_base + x)] = c;
      }
    }
    frames.add(pytraBytes(frame));
  }
  save_gif(out_path, w, h, frames, grayscale_palette(), 3, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", frames_n]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_10_plasma_effect();
}
