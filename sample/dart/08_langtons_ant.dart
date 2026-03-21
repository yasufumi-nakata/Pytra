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

// 08: Sample that outputs Langton's Ant trajectories as a GIF.

dynamic capture(dynamic grid, int w, int h) {
  var frame = pytraBytearray((w * h));
  for (var y = 0; y < h; y++) {
    int row_base = (y * w);
    for (var x = 0; x < w; x++) {
      frame[(row_base + x)] = (__pytraTruthy(grid[(y) < 0 ? grid.length + (y) : (y)][(x) < 0 ? grid[(y) < 0 ? grid.length + (y) : (y)].length + (x) : (x)]) ? (255) : (0));
    }
  }
  return pytraBytes(frame);
}

void run_08_langtons_ant() {
  int w = 420;
  int h = 420;
  String out_path = "sample/out/08_langtons_ant.gif";
  
  double start = perf_counter();
  
  var grid = (() { var __out = []; for (var unused_ = 0; unused_ < h; unused_++) { __out.add(__pytraRepeatSeq([0], w)); } return __out; })();
  int x = (w ~/ 2);
  int y = (h ~/ 2);
  int d = 0;
  
  int steps_total = 600000;
  int capture_every = 3000;
  var frames = [];
  
  for (var i = 0; i < steps_total; i++) {
    if ((grid[(y) < 0 ? grid.length + (y) : (y)][(x) < 0 ? grid[(y) < 0 ? grid.length + (y) : (y)].length + (x) : (x)] == 0)) {
      d = ((d + 1) % 4);
      grid[(y) < 0 ? grid.length + (y) : (y)][x] = 1;
    } else {
      d = ((d + 3) % 4);
      grid[(y) < 0 ? grid.length + (y) : (y)][x] = 0;
    }
    if ((d == 0)) {
      y = (((y - 1) + h) % h);
    } else {
      if ((d == 1)) {
        x = ((x + 1) % w);
      } else {
        if ((d == 2)) {
          y = ((y + 1) % h);
        } else {
          x = (((x - 1) + w) % w);
        }
      }
    }
    if (((i % capture_every) == 0)) {
      frames.add(capture(grid, w, h));
    }
  }
  save_gif(out_path, w, h, frames, grayscale_palette(), 5, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", (frames).length]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_08_langtons_ant();
}
