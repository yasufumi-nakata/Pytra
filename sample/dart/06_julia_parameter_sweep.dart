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

// 06: Sample that sweeps Julia-set parameters and outputs a GIF.

dynamic julia_palette() {
  // Keep index 0 black for points inside the set; build a high-saturation gradient for the rest.
  var palette = pytraBytearray((256 * 3));
  palette[0] = 0;
  palette[1] = 0;
  palette[2] = 0;
  for (var i = 1; i < 256; i++) {
    double t = ((i - 1) / 254.0);
    int r = pytraInt((255.0 * ((((9.0 * (1.0 - t)) * t) * t) * t)));
    int g = pytraInt((255.0 * ((((15.0 * (1.0 - t)) * (1.0 - t)) * t) * t)));
    int b = pytraInt((255.0 * ((((8.5 * (1.0 - t)) * (1.0 - t)) * (1.0 - t)) * t)));
    palette[((i * 3) + 0)] = r;
    palette[((i * 3) + 1)] = g;
    palette[((i * 3) + 2)] = b;
  }
  return pytraBytes(palette);
}

dynamic render_frame(int width, int height, double cr, double ci, int max_iter, int phase) {
  var frame = pytraBytearray((width * height));
  for (var y = 0; y < height; y++) {
    int row_base = (y * width);
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
        zy = (((2.0 * zx) * zy) + ci);
        zx = ((zx2 - zy2) + cr);
        i = ((i + 1) as int);
      }
      if ((i >= max_iter)) {
        frame[(row_base + x)] = 0;
      } else {
        // Add a small frame phase so colors flow smoothly.
        int color_index = (1 + ((((i * 224) ~/ max_iter) + phase) % 255));
        frame[(row_base + x)] = color_index;
      }
    }
  }
  return pytraBytes(frame);
}

void run_06_julia_parameter_sweep() {
  int width = 320;
  int height = 240;
  int frames_n = 72;
  int max_iter = 180;
  String out_path = "sample/out/06_julia_parameter_sweep.gif";
  
  double start = perf_counter();
  var frames = [];
  // Orbit an ellipse around a known visually good region to reduce flat blown highlights.
  double center_cr = (-0.745);
  double center_ci = 0.186;
  double radius_cr = 0.12;
  double radius_ci = 0.1;
  // Add start and phase offsets so GitHub thumbnails do not appear too dark.
  // Tune it to start in a red-leaning color range.
  int start_offset = 20;
  int phase_offset = 180;
  for (var i = 0; i < frames_n; i++) {
    double t = (((i + start_offset) % frames_n) / frames_n);
    dynamic angle = ((2.0 * math.pi) * t);
    dynamic cr = (center_cr + (radius_cr * math.cos(angle)));
    dynamic ci = (center_ci + (radius_ci * math.sin(angle)));
    int phase = ((phase_offset + (i * 5)) % 255);
    frames.add(render_frame(width, height, cr, ci, max_iter, phase));
  }
  save_gif(out_path, width, height, frames, julia_palette(), 8, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", frames_n]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_06_julia_parameter_sweep();
}
