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

// 13: Sample that outputs DFS maze-generation progress as a GIF.

dynamic capture(dynamic grid, int w, int h, int scale) {
  int width = (w * scale);
  int height = (h * scale);
  var frame = pytraBytearray((width * height));
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      int v = (__pytraTruthy((grid[(y) < 0 ? grid.length + (y) : (y)][(x) < 0 ? grid[(y) < 0 ? grid.length + (y) : (y)].length + (x) : (x)] == 0)) ? (255) : (40));
      for (var yy = 0; yy < scale; yy++) {
        int base = ((((y * scale) + yy) * width) + (x * scale));
        for (var xx = 0; xx < scale; xx++) {
          frame[(base + xx)] = v;
        }
      }
    }
  }
  return pytraBytes(frame);
}

void run_13_maze_generation_steps() {
  // Increase maze size and render resolution to ensure sufficient runtime.
  int cell_w = 89;
  int cell_h = 67;
  int scale = 5;
  int capture_every = 20;
  String out_path = "sample/out/13_maze_generation_steps.gif";
  
  double start = perf_counter();
  var grid = (() { var __out = []; for (var unused_ = 0; unused_ < cell_h; unused_++) { __out.add(__pytraRepeatSeq([1], cell_w)); } return __out; })();
  var stack = [[1, 1]];
  grid[1][1] = 0;
  
  var dirs = [[2, 0], [(-2), 0], [0, 2], [0, (-2)]];
  var frames = [];
  int step = 0;
  
  while (__pytraTruthy(stack)) {
    var __pytraTuple_1 = stack[stack.length + -1];
    var x = __pytraTuple_1[0];
    var y = __pytraTuple_1[1];
    var candidates = [];
    late dynamic nx;
    late dynamic ny;
    for (var k = 0; k < 4; k++) {
      var __pytraTuple_2 = dirs[(k) < 0 ? dirs.length + (k) : (k)];
      var dx = __pytraTuple_2[0];
      var dy = __pytraTuple_2[1];
      nx = (x + dx);
      ny = (y + dy);
      if (((nx >= 1) && (nx < (cell_w - 1)) && (ny >= 1) && (ny < (cell_h - 1)) && (grid[(ny) < 0 ? grid.length + (ny) : (ny)][(nx) < 0 ? grid[(ny) < 0 ? grid.length + (ny) : (ny)].length + (nx) : (nx)] == 1))) {
        if ((dx == 2)) {
          candidates.add([nx, ny, (x + 1), y]);
        } else {
          if ((dx == (-2))) {
            candidates.add([nx, ny, (x - 1), y]);
          } else {
            if ((dy == 2)) {
              candidates.add([nx, ny, x, (y + 1)]);
            } else {
              candidates.add([nx, ny, x, (y - 1)]);
            }
          }
        }
      }
    }
    if (((candidates).length == 0)) {
      stack.removeLast();
    } else {
      var sel = candidates[(((((x * 17) + (y * 29)) + ((stack).length * 13)) % (candidates).length)) < 0 ? candidates.length + (((((x * 17) + (y * 29)) + ((stack).length * 13)) % (candidates).length)) : (((((x * 17) + (y * 29)) + ((stack).length * 13)) % (candidates).length))];
      var __pytraTuple_3 = sel;
      nx = __pytraTuple_3[0];
      ny = __pytraTuple_3[1];
      var wx = __pytraTuple_3[2];
      var wy = __pytraTuple_3[3];
      grid[(wy) < 0 ? grid.length + (wy) : (wy)][wx] = 0;
      grid[(ny) < 0 ? grid.length + (ny) : (ny)][nx] = 0;
      stack.add([nx, ny]);
    }
    if (((step % capture_every) == 0)) {
      frames.add(capture(grid, cell_w, cell_h, scale));
    }
    step = ((step + 1) as int);
  }
  frames.add(capture(grid, cell_w, cell_h, scale));
  save_gif(out_path, (cell_w * scale), (cell_h * scale), frames, grayscale_palette(), 4, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", (frames).length]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_13_maze_generation_steps();
}
