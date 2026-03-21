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

// 01: Sample that outputs the Mandelbrot set as a PNG image.
// Syntax is kept straightforward with future transpilation in mind.

int escape_count(double cx, double cy, int max_iter) {
  double x = 0.0;
  double y = 0.0;
  for (var i = 0; i < max_iter; i++) {
    double x2 = (x * x);
    double y2 = (y * y);
    if (((x2 + y2) > 4.0)) {
      return i;
    }
    y = (((2.0 * x) * y) + cy);
    x = ((x2 - y2) + cx);
  }
  return max_iter;
}

dynamic color_map(int iter_count, int max_iter) {
  if ((iter_count >= max_iter)) {
    return [0, 0, 0];
  }
  double t = (iter_count / max_iter);
  int r = pytraInt((255.0 * (t * t)));
  int g = pytraInt((255.0 * t));
  int b = pytraInt((255.0 * (1.0 - t)));
  return [r, g, b];
}

dynamic render_mandelbrot(int width, int height, int max_iter, double x_min, double x_max, double y_min, double y_max) {
  var pixels = <int>[];
  
  for (var y = 0; y < height; y++) {
    double py = (y_min + ((y_max - y_min) * (y / (height - 1))));
    
    for (var x = 0; x < width; x++) {
      double px = (x_min + ((x_max - x_min) * (x / (width - 1))));
      int it = escape_count(px, py, max_iter);
      int r;
      int g;
      int b;
      if ((it >= max_iter)) {
        r = 0;
        g = 0;
        b = 0;
      } else {
        double t = (it / max_iter);
        r = pytraInt((255.0 * (t * t)));
        g = pytraInt((255.0 * t));
        b = pytraInt((255.0 * (1.0 - t)));
      }
      pixels.add(r);
      pixels.add(g);
      pixels.add(b);
    }
  }
  return pixels;
}

void run_mandelbrot() {
  int width = 1600;
  int height = 1200;
  int max_iter = 1000;
  String out_path = "sample/out/01_mandelbrot.png";
  
  double start = perf_counter();
  
  var pixels = render_mandelbrot(width, height, max_iter, (-2.2), 1.0, (-1.2), 1.2);
  png.write_rgb_png(out_path, width, height, pixels);
  
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["size:", width, "x", height]);
  __pytraPrint(["max_iter:", max_iter]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_mandelbrot();
}
