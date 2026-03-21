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

// 11: Sample that outputs Lissajous-motion particles as a GIF.

dynamic color_palette() {
  var p = <int>[];
  for (var i = 0; i < 256; i++) {
    int r = i;
    int g = ((i * 3) % 256);
    int b = (255 - i);
    p.add(r);
    p.add(g);
    p.add(b);
  }
  return pytraBytes(p);
}

void run_11_lissajous_particles() {
  int w = 320;
  int h = 240;
  int frames_n = 360;
  int particles = 48;
  String out_path = "sample/out/11_lissajous_particles.gif";
  
  double start = perf_counter();
  var frames = [];
  
  for (var t = 0; t < frames_n; t++) {
    var frame = pytraBytearray((w * h));
    
    for (var p = 0; p < particles; p++) {
      double phase = (p * 0.261799);
      int x = pytraInt(((w * 0.5) + ((w * 0.38) * math.sin(((0.11 * t) + (phase * 2.0))))));
      int y = pytraInt(((h * 0.5) + ((h * 0.38) * math.sin(((0.17 * t) + (phase * 3.0))))));
      int color = (30 + ((p * 9) % 220));
      
      for (var dy = (-2); dy < 3; dy++) {
        for (var dx = (-2); dx < 3; dx++) {
          int xx = (x + dx);
          int yy = (y + dy);
          if (((xx >= 0) && (xx < w) && (yy >= 0) && (yy < h))) {
            int d2 = ((dx * dx) + (dy * dy));
            if ((d2 <= 4)) {
              int idx = ((yy * w) + xx);
              int v = (color - (d2 * 20));
              v = ((0) > (v) ? (0) : (v));
              if ((v > frame[(idx) < 0 ? frame.length + (idx) : (idx)])) {
                frame[idx] = v;
              }
            }
          }
        }
      }
    }
    frames.add(pytraBytes(frame));
  }
  save_gif(out_path, w, h, frames, color_palette(), 3, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", frames_n]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_11_lissajous_particles();
}
