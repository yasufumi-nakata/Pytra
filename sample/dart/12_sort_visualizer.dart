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

// 12: Sample that outputs intermediate states of bubble sort as a GIF.

dynamic render(dynamic values, int w, int h) {
  var frame = pytraBytearray((w * h));
  int n = (values).length;
  double bar_w = (w / n);
  for (var i = 0; i < n; i++) {
    int x0 = pytraInt((i * bar_w));
    int x1 = pytraInt(((i + 1) * bar_w));
    if ((x1 <= x0)) {
      x1 = (x0 + 1);
    }
    int bh = pytraInt(((values[(i) < 0 ? values.length + (i) : (i)] / n) * h));
    int y = (h - bh);
    var __forStart_1 = y;
    for (var y = __forStart_1; y < h; y++) {
      for (var x = x0; x < x1; x++) {
        frame[((y * w) + x)] = 255;
      }
    }
  }
  return pytraBytes(frame);
}

void run_12_sort_visualizer() {
  int w = 320;
  int h = 180;
  int n = 124;
  String out_path = "sample/out/12_sort_visualizer.gif";
  
  double start = perf_counter();
  var values = [];
  for (var i = 0; i < n; i++) {
    values.add((((i * 37) + 19) % n));
  }
  var frames = [render(values, w, h)];
  int frame_stride = 16;
  
  int op = 0;
  for (var i = 0; i < n; i++) {
    bool swapped = false;
    for (var j = 0; j < ((n - i) - 1); j++) {
      if ((values[(j) < 0 ? values.length + (j) : (j)] > values[((j + 1)) < 0 ? values.length + ((j + 1)) : ((j + 1))])) {
        var __pytraTuple_2 = [values[((j + 1)) < 0 ? values.length + ((j + 1)) : ((j + 1))], values[(j) < 0 ? values.length + (j) : (j)]];
        values[j] = __pytraTuple_2[0];
        values[(j + 1)] = __pytraTuple_2[1];
        swapped = true;
      }
      if (((op % frame_stride) == 0)) {
        frames.add(render(values, w, h));
      }
      op = ((op + 1) as int);
    }
    if ((!swapped)) {
      break;
    }
  }
  save_gif(out_path, w, h, frames, grayscale_palette(), 3, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", (frames).length]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_12_sort_visualizer();
}
