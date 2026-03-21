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

// 14: Sample that outputs a moving-light scene in a simple raymarching style as a GIF.

dynamic palette() {
  var p = <int>[];
  for (var i = 0; i < 256; i++) {
    dynamic r = ((255) < (pytraInt((20 + (i * 0.9)))) ? (255) : (pytraInt((20 + (i * 0.9)))));
    dynamic g = ((255) < (pytraInt((10 + (i * 0.7)))) ? (255) : (pytraInt((10 + (i * 0.7)))));
    dynamic b = ((255) < ((30 + i)) ? (255) : ((30 + i)));
    p.add(r);
    p.add(g);
    p.add(b);
  }
  return pytraBytes(p);
}

int scene(double x, double y, double light_x, double light_y) {
  double x1 = (x + 0.45);
  double y1 = (y + 0.2);
  double x2 = (x - 0.35);
  double y2 = (y - 0.15);
  dynamic r1 = math.sqrt(((x1 * x1) + (y1 * y1)));
  dynamic r2 = math.sqrt(((x2 * x2) + (y2 * y2)));
  dynamic blob = (math.exp((((-7.0) * r1) * r1)) + math.exp((((-8.0) * r2) * r2)));
  
  double lx = (x - light_x);
  double ly = (y - light_y);
  dynamic l = math.sqrt(((lx * lx) + (ly * ly)));
  dynamic lit = (1.0 / (1.0 + ((3.5 * l) * l)));
  
  int v = pytraInt((((255.0 * blob) * lit) * 5.0));
  return ((255) < (((0) > (v) ? (0) : (v))) ? (255) : (((0) > (v) ? (0) : (v))));
}

void run_14_raymarching_light_cycle() {
  int w = 320;
  int h = 240;
  int frames_n = 84;
  String out_path = "sample/out/14_raymarching_light_cycle.gif";
  
  double start = perf_counter();
  var frames = [];
  
  for (var t = 0; t < frames_n; t++) {
    var frame = pytraBytearray((w * h));
    dynamic a = (((t / frames_n) * math.pi) * 2.0);
    dynamic light_x = (0.75 * math.cos(a));
    dynamic light_y = (0.55 * math.sin((a * 1.2)));
    
    for (var y = 0; y < h; y++) {
      int row_base = (y * w);
      double py = (((y / (h - 1)) * 2.0) - 1.0);
      for (var x = 0; x < w; x++) {
        double px = (((x / (w - 1)) * 2.0) - 1.0);
        frame[(row_base + x)] = scene(px, py, light_x, light_y);
      }
    }
    frames.add(pytraBytes(frame));
  }
  save_gif(out_path, w, h, frames, palette(), 3, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", frames_n]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_14_raymarching_light_cycle();
}
