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

// 07: Sample that outputs Game of Life evolution as a GIF.

dynamic next_state(dynamic grid, int w, int h) {
  var nxt = [];
  for (var y = 0; y < h; y++) {
    var row = [];
    for (var x = 0; x < w; x++) {
      int cnt = 0;
      for (var dy = (-1); dy < 2; dy++) {
        for (var dx = (-1); dx < 2; dx++) {
          if (((dx != 0) || (dy != 0))) {
            int nx = (((x + dx) + w) % w);
            int ny = (((y + dy) + h) % h);
            cnt = ((cnt + grid[(ny) < 0 ? grid.length + (ny) : (ny)][(nx) < 0 ? grid[(ny) < 0 ? grid.length + (ny) : (ny)].length + (nx) : (nx)]) as int);
          }
        }
      }
      int alive = grid[(y) < 0 ? grid.length + (y) : (y)][(x) < 0 ? grid[(y) < 0 ? grid.length + (y) : (y)].length + (x) : (x)];
      if (((alive == 1) && ((cnt == 2) || (cnt == 3)))) {
        row.add(1);
      } else {
        if (((alive == 0) && (cnt == 3))) {
          row.add(1);
        } else {
          row.add(0);
        }
      }
    }
    nxt.add(row);
  }
  return nxt;
}

dynamic render(dynamic grid, int w, int h, int cell) {
  int width = (w * cell);
  int height = (h * cell);
  var frame = pytraBytearray((width * height));
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      int v = (__pytraTruthy(grid[(y) < 0 ? grid.length + (y) : (y)][(x) < 0 ? grid[(y) < 0 ? grid.length + (y) : (y)].length + (x) : (x)]) ? (255) : (0));
      for (var yy = 0; yy < cell; yy++) {
        int base = ((((y * cell) + yy) * width) + (x * cell));
        for (var xx = 0; xx < cell; xx++) {
          frame[(base + xx)] = v;
        }
      }
    }
  }
  return pytraBytes(frame);
}

void run_07_game_of_life_loop() {
  int w = 144;
  int h = 108;
  int cell = 4;
  int steps = 105;
  String out_path = "sample/out/07_game_of_life_loop.gif";
  
  double start = perf_counter();
  var grid = (() { var __out = []; for (var unused_ = 0; unused_ < h; unused_++) { __out.add(__pytraRepeatSeq([0], w)); } return __out; })();
  
  // Lay down sparse noise so the whole field is less likely to stabilize too early.
  // Avoid large integer literals so all transpilers handle the expression consistently.
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      int noise = (((((x * 37) + (y * 73)) + ((x * y) % 19)) + ((x + y) % 11)) % 97);
      if ((noise < 3)) {
        grid[(y) < 0 ? grid.length + (y) : (y)][x] = 1;
      }
    }
  }
  // Place multiple well-known long-lived patterns.
  var glider = [[0, 1, 0], [0, 0, 1], [1, 1, 1]];
  var r_pentomino = [[0, 1, 1], [1, 1, 0], [0, 1, 0]];
  var lwss = [[0, 1, 1, 1, 1], [1, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 0, 0, 1, 0]];
  
  for (var gy = 8; gy < (h - 8); gy += 18) {
    for (var gx = 8; gx < (w - 8); gx += 22) {
      int kind = (((gx * 7) + (gy * 11)) % 3);
      int ph;
      int pw;
      if ((kind == 0)) {
        ph = (glider).length;
        for (var py = 0; py < ph; py++) {
          pw = (glider[(py) < 0 ? glider.length + (py) : (py)]).length;
          for (var px = 0; px < pw; px++) {
            if ((glider[(py) < 0 ? glider.length + (py) : (py)][(px) < 0 ? glider[(py) < 0 ? glider.length + (py) : (py)].length + (px) : (px)] == 1)) {
              grid[(((gy + py) % h)) < 0 ? grid.length + (((gy + py) % h)) : (((gy + py) % h))][((gx + px) % w)] = 1;
            }
          }
        }
      } else {
        if ((kind == 1)) {
          ph = (r_pentomino).length;
          for (var py = 0; py < ph; py++) {
            pw = (r_pentomino[(py) < 0 ? r_pentomino.length + (py) : (py)]).length;
            for (var px = 0; px < pw; px++) {
              if ((r_pentomino[(py) < 0 ? r_pentomino.length + (py) : (py)][(px) < 0 ? r_pentomino[(py) < 0 ? r_pentomino.length + (py) : (py)].length + (px) : (px)] == 1)) {
                grid[(((gy + py) % h)) < 0 ? grid.length + (((gy + py) % h)) : (((gy + py) % h))][((gx + px) % w)] = 1;
              }
            }
          }
        } else {
          ph = (lwss).length;
          for (var py = 0; py < ph; py++) {
            pw = (lwss[(py) < 0 ? lwss.length + (py) : (py)]).length;
            for (var px = 0; px < pw; px++) {
              if ((lwss[(py) < 0 ? lwss.length + (py) : (py)][(px) < 0 ? lwss[(py) < 0 ? lwss.length + (py) : (py)].length + (px) : (px)] == 1)) {
                grid[(((gy + py) % h)) < 0 ? grid.length + (((gy + py) % h)) : (((gy + py) % h))][((gx + px) % w)] = 1;
              }
            }
          }
        }
      }
    }
  }
  var frames = [];
  for (var unused_ = 0; unused_ < steps; unused_++) {
    frames.add(render(grid, w, h, cell));
    grid = next_state(grid, w, h);
  }
  save_gif(out_path, (w * cell), (h * cell), frames, grayscale_palette(), 4, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", steps]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_07_game_of_life_loop();
}
