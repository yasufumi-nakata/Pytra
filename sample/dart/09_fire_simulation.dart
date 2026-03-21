import 'py_runtime.dart';
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

// 09: Sample that outputs a simple fire effect as a GIF.

dynamic fire_palette() {
  var p = <int>[];
  for (var i = 0; i < 256; i++) {
    int r = 0;
    int g = 0;
    int b = 0;
    if ((i < 85)) {
      r = (i * 3);
      g = 0;
      b = 0;
    } else {
      if ((i < 170)) {
        r = 255;
        g = ((i - 85) * 3);
        b = 0;
      } else {
        r = 255;
        g = 255;
        b = ((i - 170) * 3);
      }
    }
    p.add(r);
    p.add(g);
    p.add(b);
  }
  return pytraBytes(p);
}

void run_09_fire_simulation() {
  int w = 380;
  int h = 260;
  int steps = 420;
  String out_path = "sample/out/09_fire_simulation.gif";
  
  double start = perf_counter();
  var heat = (() { var __out = []; for (var unused_ = 0; unused_ < h; unused_++) { __out.add(__pytraRepeatSeq([0], w)); } return __out; })();
  var frames = [];
  
  for (var t = 0; t < steps; t++) {
    for (var x = 0; x < w; x++) {
      int val = (170 + (((x * 13) + (t * 17)) % 86));
      heat[((h - 1)) < 0 ? heat.length + ((h - 1)) : ((h - 1))][x] = val;
    }
    for (var y = 1; y < h; y++) {
      for (var x = 0; x < w; x++) {
        int a = heat[(y) < 0 ? heat.length + (y) : (y)][(x) < 0 ? heat[(y) < 0 ? heat.length + (y) : (y)].length + (x) : (x)];
        int b = heat[(y) < 0 ? heat.length + (y) : (y)][((((x - 1) + w) % w)) < 0 ? heat[(y) < 0 ? heat.length + (y) : (y)].length + ((((x - 1) + w) % w)) : ((((x - 1) + w) % w))];
        int c = heat[(y) < 0 ? heat.length + (y) : (y)][(((x + 1) % w)) < 0 ? heat[(y) < 0 ? heat.length + (y) : (y)].length + (((x + 1) % w)) : (((x + 1) % w))];
        int d = heat[(((y + 1) % h)) < 0 ? heat.length + (((y + 1) % h)) : (((y + 1) % h))][(x) < 0 ? heat[(((y + 1) % h)) < 0 ? heat.length + (((y + 1) % h)) : (((y + 1) % h))].length + (x) : (x)];
        int v = ((((a + b) + c) + d) ~/ 4);
        int cool = (1 + (((x + y) + t) % 3));
        int nv = (v - cool);
        heat[((y - 1)) < 0 ? heat.length + ((y - 1)) : ((y - 1))][x] = (__pytraTruthy((nv > 0)) ? (nv) : (0));
      }
    }
    var frame = pytraBytearray((w * h));
    for (var yy = 0; yy < h; yy++) {
      int row_base = (yy * w);
      for (var xx = 0; xx < w; xx++) {
        frame[(row_base + xx)] = heat[(yy) < 0 ? heat.length + (yy) : (yy)][(xx) < 0 ? heat[(yy) < 0 ? heat.length + (yy) : (yy)].length + (xx) : (xx)];
      }
    }
    frames.add(pytraBytes(frame));
  }
  save_gif(out_path, w, h, frames, fire_palette(), 4, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", steps]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_09_fire_simulation();
}
