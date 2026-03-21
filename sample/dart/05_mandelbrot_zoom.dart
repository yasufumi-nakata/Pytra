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

// 05: Sample that outputs a Mandelbrot zoom as an animated GIF.

dynamic render_frame(int width, int height, double center_x, double center_y, double scale, int max_iter) {
  var frame = pytraBytearray((width * height));
  for (var y = 0; y < height; y++) {
    int row_base = (y * width);
    double cy = (center_y + ((y - (height * 0.5)) * scale));
    for (var x = 0; x < width; x++) {
      double cx = (center_x + ((x - (width * 0.5)) * scale));
      double zx = 0.0;
      double zy = 0.0;
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
      frame[(row_base + x)] = pytraInt(((255.0 * i) / max_iter));
    }
  }
  return pytraBytes(frame);
}

void run_05_mandelbrot_zoom() {
  int width = 320;
  int height = 240;
  int frame_count = 48;
  int max_iter = 110;
  double center_x = (-0.743643887037151);
  double center_y = 0.13182590420533;
  double base_scale = (3.2 / width);
  double zoom_per_frame = 0.93;
  String out_path = "sample/out/05_mandelbrot_zoom.gif";
  
  double start = perf_counter();
  var frames = [];
  double scale = base_scale;
  for (var unused_ = 0; unused_ < frame_count; unused_++) {
    frames.add(render_frame(width, height, center_x, center_y, scale, max_iter));
    scale *= zoom_per_frame;
  }
  save_gif(out_path, width, height, frames, grayscale_palette(), 5, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", frame_count]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_05_mandelbrot_zoom();
}
