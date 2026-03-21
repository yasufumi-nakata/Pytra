import 'py_runtime.dart';
import 'png/east.dart' as png;


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

// 03: Sample that outputs a Julia set as a PNG image.
// Implemented with simple loop-centric logic for transpilation compatibility.

dynamic render_julia(int width, int height, int max_iter, double cx, double cy) {
  var pixels = <int>[];
  
  for (var y = 0; y < height; y++) {
    double zy0 = ((-1.2) + (2.4 * (y / (height - 1))));
    
    for (var x = 0; x < width; x++) {
      double zx = ((-1.8) + (3.6 * (x / (width - 1))));
      double zy = zy0;
      
      int i = 0;
      while ((i < max_iter)) {
        double zx2 = (zx * zx);
        double zy2 = (zy * zy);
        if (((zx2 + zy2) > 4.0)) {
          break;
        }
        zy = (((2.0 * zx) * zy) + cy);
        zx = ((zx2 - zy2) + cx);
        i = ((i + 1) as int);
      }
      int r = 0;
      int g = 0;
      int b = 0;
      if ((i >= max_iter)) {
        r = 0;
        g = 0;
        b = 0;
      } else {
        double t = (i / max_iter);
        r = pytraInt((255.0 * (0.2 + (0.8 * t))));
        g = pytraInt((255.0 * (0.1 + (0.9 * (t * t)))));
        b = pytraInt((255.0 * (1.0 - t)));
      }
      pixels.add(r);
      pixels.add(g);
      pixels.add(b);
    }
  }
  return pixels;
}

void run_julia() {
  int width = 3840;
  int height = 2160;
  int max_iter = 20000;
  String out_path = "sample/out/03_julia_set.png";
  
  double start = perf_counter();
  var pixels = render_julia(width, height, max_iter, (-0.8), 0.156);
  png.write_rgb_png(out_path, width, height, pixels);
  double elapsed = (perf_counter() - start);
  
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["size:", width, "x", height]);
  __pytraPrint(["max_iter:", max_iter]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_julia();
}
