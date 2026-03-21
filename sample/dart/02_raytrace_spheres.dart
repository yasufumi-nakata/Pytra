import 'py_runtime.dart';
import 'dart:math' as math;
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

// 02: Sample that runs a mini sphere-only ray tracer and outputs a PNG image.
// Dependencies are kept minimal (time only) for transpilation compatibility.

double clamp01(double v) {
  if ((v < 0.0)) {
    return 0.0;
  }
  if ((v > 1.0)) {
    return 1.0;
  }
  return v;
}

double hit_sphere(double ox, double oy, double oz, double dx, double dy, double dz, double cx, double cy, double cz, double r) {
  double lx = (ox - cx);
  double ly = (oy - cy);
  double lz = (oz - cz);
  
  double a = (((dx * dx) + (dy * dy)) + (dz * dz));
  double b = (2.0 * (((lx * dx) + (ly * dy)) + (lz * dz)));
  double c = ((((lx * lx) + (ly * ly)) + (lz * lz)) - (r * r));
  
  double d = ((b * b) - ((4.0 * a) * c));
  if ((d < 0.0)) {
    return (-1.0);
  }
  double sd = math.sqrt(d);
  double t0 = (((-b) - sd) / (2.0 * a));
  double t1 = (((-b) + sd) / (2.0 * a));
  
  if ((t0 > 0.001)) {
    return t0;
  }
  if ((t1 > 0.001)) {
    return t1;
  }
  return (-1.0);
}

dynamic render(int width, int height, int aa) {
  var pixels = <int>[];
  
  // Camera origin
  double ox = 0.0;
  double oy = 0.0;
  double oz = (-3.0);
  
  // Light direction (normalized)
  double lx = (-0.4);
  double ly = 0.8;
  double lz = (-0.45);
  
  for (var y = 0; y < height; y++) {
    for (var x = 0; x < width; x++) {
      int ar = 0;
      int ag = 0;
      int ab = 0;
      
      for (var ay = 0; ay < aa; ay++) {
        for (var ax = 0; ax < aa; ax++) {
          double fy = ((y + ((ay + 0.5) / aa)) / (height - 1));
          double fx = ((x + ((ax + 0.5) / aa)) / (width - 1));
          double sy = (1.0 - (2.0 * fy));
          double sx = (((2.0 * fx) - 1.0) * (width / height));
          
          double dx = sx;
          double dy = sy;
          double dz = 1.0;
          double inv_len = (1.0 / math.sqrt((((dx * dx) + (dy * dy)) + (dz * dz))));
          dx *= inv_len;
          dy *= inv_len;
          dz *= inv_len;
          
          double t_min = 1e+30;
          int hit_id = (-1);
          
          double t = hit_sphere(ox, oy, oz, dx, dy, dz, (-0.8), (-0.2), 2.2, 0.8);
          if (((t > 0.0) && (t < t_min))) {
            t_min = t;
            hit_id = 0;
          }
          t = hit_sphere(ox, oy, oz, dx, dy, dz, 0.9, 0.1, 2.9, 0.95);
          if (((t > 0.0) && (t < t_min))) {
            t_min = t;
            hit_id = 1;
          }
          t = hit_sphere(ox, oy, oz, dx, dy, dz, 0.0, (-1001.0), 3.0, 1000.0);
          if (((t > 0.0) && (t < t_min))) {
            t_min = t;
            hit_id = 2;
          }
          int r = 0;
          int g = 0;
          int b = 0;
          
          if ((hit_id >= 0)) {
            double px = (ox + (dx * t_min));
            double py = (oy + (dy * t_min));
            double pz = (oz + (dz * t_min));
            
            double nx = 0.0;
            double ny = 0.0;
            double nz = 0.0;
            
            if ((hit_id == 0)) {
              nx = ((px + 0.8) / 0.8);
              ny = ((py + 0.2) / 0.8);
              nz = ((pz - 2.2) / 0.8);
            } else {
              if ((hit_id == 1)) {
                nx = ((px - 0.9) / 0.95);
                ny = ((py - 0.1) / 0.95);
                nz = ((pz - 2.9) / 0.95);
              } else {
                nx = 0.0;
                ny = 1.0;
                nz = 0.0;
              }
            }
            double diff = (((nx * (-lx)) + (ny * (-ly))) + (nz * (-lz)));
            diff = clamp01(diff);
            
            double base_r = 0.0;
            double base_g = 0.0;
            double base_b = 0.0;
            
            if ((hit_id == 0)) {
              base_r = 0.95;
              base_g = 0.35;
              base_b = 0.25;
            } else {
              if ((hit_id == 1)) {
                base_r = 0.25;
                base_g = 0.55;
                base_b = 0.95;
              } else {
                int checker = (pytraInt(((px + 50.0) * 0.8)) + pytraInt(((pz + 50.0) * 0.8)));
                if (((checker % 2) == 0)) {
                  base_r = 0.85;
                  base_g = 0.85;
                  base_b = 0.85;
                } else {
                  base_r = 0.2;
                  base_g = 0.2;
                  base_b = 0.2;
                }
              }
            }
            double shade = (0.12 + (0.88 * diff));
            r = pytraInt((255.0 * clamp01((base_r * shade))));
            g = pytraInt((255.0 * clamp01((base_g * shade))));
            b = pytraInt((255.0 * clamp01((base_b * shade))));
          } else {
            double tsky = (0.5 * (dy + 1.0));
            r = pytraInt((255.0 * (0.65 + (0.2 * tsky))));
            g = pytraInt((255.0 * (0.75 + (0.18 * tsky))));
            b = pytraInt((255.0 * (0.9 + (0.08 * tsky))));
          }
          ar = ((ar + r) as int);
          ag = ((ag + g) as int);
          ab = ((ab + b) as int);
        }
      }
      int samples = (aa * aa);
      pixels.add((ar ~/ samples));
      pixels.add((ag ~/ samples));
      pixels.add((ab ~/ samples));
    }
  }
  return pixels;
}

void run_raytrace() {
  int width = 1600;
  int height = 900;
  int aa = 2;
  String out_path = "sample/out/02_raytrace_spheres.png";
  
  double start = perf_counter();
  var pixels = render(width, height, aa);
  png.write_rgb_png(out_path, width, height, pixels);
  double elapsed = (perf_counter() - start);
  
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["size:", width, "x", height]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_raytrace();
}
