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

// 16: Sample that ray-traces chaotic rotation of glass sculptures and outputs a GIF.

double clamp01(double v) {
  if ((v < 0.0)) {
    return 0.0;
  }
  if ((v > 1.0)) {
    return 1.0;
  }
  return v;
}

double dot(double ax, double ay, double az, double bx, double by, double bz) {
  return (((ax * bx) + (ay * by)) + (az * bz));
}

double length(double x, double y, double z) {
  return math.sqrt((((x * x) + (y * y)) + (z * z)));
}

dynamic normalize(double x, double y, double z) {
  double l = length(x, y, z);
  if ((l < 1e-09)) {
    return [0.0, 0.0, 0.0];
  }
  return [(x / l), (y / l), (z / l)];
}

dynamic reflect(double ix, double iy, double iz, double nx, double ny, double nz) {
  double d = (dot(ix, iy, iz, nx, ny, nz) * 2.0);
  return [(ix - (d * nx)), (iy - (d * ny)), (iz - (d * nz))];
}

dynamic refract(double ix, double iy, double iz, double nx, double ny, double nz, double eta) {
  // Simple IOR-based refraction. Return reflection direction on total internal reflection.
  double cosi = (-dot(ix, iy, iz, nx, ny, nz));
  double sint2 = ((eta * eta) * (1.0 - (cosi * cosi)));
  if ((sint2 > 1.0)) {
    return reflect(ix, iy, iz, nx, ny, nz);
  }
  dynamic cost = math.sqrt((1.0 - sint2));
  dynamic k = ((eta * cosi) - cost);
  return [((eta * ix) + (k * nx)), ((eta * iy) + (k * ny)), ((eta * iz) + (k * nz))];
}

double schlick(double cos_theta, double f0) {
  double m = (1.0 - cos_theta);
  return (f0 + ((1.0 - f0) * ((((m * m) * m) * m) * m)));
}

dynamic sky_color(double dx, double dy, double dz, double tphase) {
  // Sky gradient + neon band
  double t = (0.5 * (dy + 1.0));
  double r = (0.06 + (0.2 * t));
  double g = (0.1 + (0.25 * t));
  double b = (0.16 + (0.45 * t));
  dynamic band = (0.5 + (0.5 * math.sin((((8.0 * dx) + (6.0 * dz)) + tphase))));
  r += (0.08 * band);
  g += (0.05 * band);
  b += (0.12 * band);
  return [clamp01(r), clamp01(g), clamp01(b)];
}

double sphere_intersect(double ox, double oy, double oz, double dx, double dy, double dz, double cx, double cy, double cz, double radius) {
  double lx = (ox - cx);
  double ly = (oy - cy);
  double lz = (oz - cz);
  double b = (((lx * dx) + (ly * dy)) + (lz * dz));
  double c = ((((lx * lx) + (ly * ly)) + (lz * lz)) - (radius * radius));
  double h = ((b * b) - c);
  if ((h < 0.0)) {
    return (-1.0);
  }
  dynamic s = math.sqrt(h);
  dynamic t0 = ((-b) - s);
  if ((t0 > 0.0001)) {
    return t0;
  }
  dynamic t1 = ((-b) + s);
  if ((t1 > 0.0001)) {
    return t1;
  }
  return (-1.0);
}

dynamic palette_332() {
  // 3-3-2 quantized palette. Lightweight quantization that stays fast after transpilation.
  var p = pytraBytearray((256 * 3));
  for (var i = 0; i < 256; i++) {
    int r = ((i >> 5) & 7);
    int g = ((i >> 2) & 7);
    int b = (i & 3);
    p[((i * 3) + 0)] = pytraInt(((255 * r) / 7));
    p[((i * 3) + 1)] = pytraInt(((255 * g) / 7));
    p[((i * 3) + 2)] = pytraInt(((255 * b) / 3));
  }
  return pytraBytes(p);
}

int quantize_332(double r, double g, double b) {
  int rr = pytraInt((clamp01(r) * 255.0));
  int gg = pytraInt((clamp01(g) * 255.0));
  int bb = pytraInt((clamp01(b) * 255.0));
  return ((((rr >> 5) << 5) + ((gg >> 5) << 2)) + (bb >> 6));
}

dynamic render_frame(int width, int height, int frame_id, int frames_n) {
  double t = (frame_id / frames_n);
  dynamic tphase = ((2.0 * math.pi) * t);
  
  // Camera slowly orbits.
  double cam_r = 3.0;
  dynamic cam_x = (cam_r * math.cos((tphase * 0.9)));
  dynamic cam_y = (1.1 + (0.25 * math.sin((tphase * 0.6))));
  dynamic cam_z = (cam_r * math.sin((tphase * 0.9)));
  double look_x = 0.0;
  double look_y = 0.35;
  double look_z = 0.0;
  
  var __pytraTuple_1 = normalize((look_x - cam_x), (look_y - cam_y), (look_z - cam_z));
  var fwd_x = __pytraTuple_1[0];
  var fwd_y = __pytraTuple_1[1];
  var fwd_z = __pytraTuple_1[2];
  var __pytraTuple_2 = normalize(fwd_z, 0.0, (-fwd_x));
  var right_x = __pytraTuple_2[0];
  var right_y = __pytraTuple_2[1];
  var right_z = __pytraTuple_2[2];
  var __pytraTuple_3 = normalize(((right_y * fwd_z) - (right_z * fwd_y)), ((right_z * fwd_x) - (right_x * fwd_z)), ((right_x * fwd_y) - (right_y * fwd_x)));
  var up_x = __pytraTuple_3[0];
  var up_y = __pytraTuple_3[1];
  var up_z = __pytraTuple_3[2];
  
  // Moving glass sculpture (3 spheres) and an emissive sphere.
  dynamic s0x = (0.9 * math.cos((1.3 * tphase)));
  dynamic s0y = (0.15 + (0.35 * math.sin((1.7 * tphase))));
  dynamic s0z = (0.9 * math.sin((1.3 * tphase)));
  dynamic s1x = (1.2 * math.cos(((1.3 * tphase) + 2.094)));
  dynamic s1y = (0.1 + (0.4 * math.sin(((1.1 * tphase) + 0.8))));
  dynamic s1z = (1.2 * math.sin(((1.3 * tphase) + 2.094)));
  dynamic s2x = (1.0 * math.cos(((1.3 * tphase) + 4.188)));
  dynamic s2y = (0.2 + (0.3 * math.sin(((1.5 * tphase) + 1.9))));
  dynamic s2z = (1.0 * math.sin(((1.3 * tphase) + 4.188)));
  double lr = 0.35;
  dynamic lx = (2.4 * math.cos((tphase * 1.8)));
  dynamic ly = (1.8 + (0.8 * math.sin((tphase * 1.2))));
  dynamic lz = (2.4 * math.sin((tphase * 1.8)));
  
  var frame = pytraBytearray((width * height));
  double aspect = (width / height);
  double fov = 1.25;
  
  for (var py = 0; py < height; py++) {
    int row_base = (py * width);
    double sy = (1.0 - ((2.0 * (py + 0.5)) / height));
    for (var px = 0; px < width; px++) {
      double sx = ((((2.0 * (px + 0.5)) / width) - 1.0) * aspect);
      dynamic rx = (fwd_x + (fov * ((sx * right_x) + (sy * up_x))));
      dynamic ry = (fwd_y + (fov * ((sx * right_y) + (sy * up_y))));
      dynamic rz = (fwd_z + (fov * ((sx * right_z) + (sy * up_z))));
      var __pytraTuple_4 = normalize(rx, ry, rz);
      var dx = __pytraTuple_4[0];
      var dy = __pytraTuple_4[1];
      var dz = __pytraTuple_4[2];
      
      // Search for the nearest hit.
      double best_t = 1000000000.0;
      int hit_kind = 0;
      double r = 0.0;
      double g = 0.0;
      double b = 0.0;
      
      // Floor plane y=-1.2
      if ((dy < (-1e-06))) {
        dynamic tf = (((-1.2) - cam_y) / dy);
        if (((tf > 0.0001) && (tf < best_t))) {
          best_t = tf;
          hit_kind = 1;
        }
      }
      double t0 = sphere_intersect(cam_x, cam_y, cam_z, dx, dy, dz, s0x, s0y, s0z, 0.65);
      if (((t0 > 0.0) && (t0 < best_t))) {
        best_t = t0;
        hit_kind = 2;
      }
      double t1 = sphere_intersect(cam_x, cam_y, cam_z, dx, dy, dz, s1x, s1y, s1z, 0.72);
      if (((t1 > 0.0) && (t1 < best_t))) {
        best_t = t1;
        hit_kind = 3;
      }
      double t2 = sphere_intersect(cam_x, cam_y, cam_z, dx, dy, dz, s2x, s2y, s2z, 0.58);
      if (((t2 > 0.0) && (t2 < best_t))) {
        best_t = t2;
        hit_kind = 4;
      }
      late dynamic glow;
      late dynamic hx;
      late dynamic hz;
      double ldx;
      double ldy;
      double ldz;
      late dynamic lxv;
      late dynamic lyv;
      late dynamic lzv;
      late dynamic ndotl;
      if ((hit_kind == 0)) {
        var __pytraTuple_5 = sky_color(dx, dy, dz, tphase);
        r = __pytraTuple_5[0];
        g = __pytraTuple_5[1];
        b = __pytraTuple_5[2];
      } else {
        if ((hit_kind == 1)) {
          hx = (cam_x + (best_t * dx));
          hz = (cam_z + (best_t * dz));
          int cx_i = pytraInt(((hx * 2.0) as num).floor());
          int cz_i = pytraInt(((hz * 2.0) as num).floor());
          int checker = (__pytraTruthy((((cx_i + cz_i) % 2) == 0)) ? (0) : (1));
          double base_r = (__pytraTruthy((checker == 0)) ? (0.1) : (0.04));
          double base_g = (__pytraTruthy((checker == 0)) ? (0.11) : (0.05));
          double base_b = (__pytraTruthy((checker == 0)) ? (0.13) : (0.08));
          // Emissive sphere contribution.
          lxv = (lx - hx);
          lyv = (ly - (-1.2));
          lzv = (lz - hz);
          var __pytraTuple_6 = normalize(lxv, lyv, lzv);
          ldx = __pytraTuple_6[0];
          ldy = __pytraTuple_6[1];
          ldz = __pytraTuple_6[2];
          ndotl = ((ldy) > (0.0) ? (ldy) : (0.0));
          dynamic ldist2 = (((lxv * lxv) + (lyv * lyv)) + (lzv * lzv));
          glow = (8.0 / (1.0 + ldist2));
          r = ((base_r + (0.8 * glow)) + (0.2 * ndotl));
          g = ((base_g + (0.5 * glow)) + (0.18 * ndotl));
          b = ((base_b + (1.0 * glow)) + (0.24 * ndotl));
        } else {
          double cx = 0.0;
          double cy = 0.0;
          double cz = 0.0;
          double rad = 1.0;
          if ((hit_kind == 2)) {
            cx = s0x;
            cy = s0y;
            cz = s0z;
            rad = 0.65;
          } else {
            if ((hit_kind == 3)) {
              cx = s1x;
              cy = s1y;
              cz = s1z;
              rad = 0.72;
            } else {
              cx = s2x;
              cy = s2y;
              cz = s2z;
              rad = 0.58;
            }
          }
          hx = (cam_x + (best_t * dx));
          dynamic hy = (cam_y + (best_t * dy));
          hz = (cam_z + (best_t * dz));
          var __pytraTuple_7 = normalize(((hx - cx) / rad), ((hy - cy) / rad), ((hz - cz) / rad));
          var nx = __pytraTuple_7[0];
          var ny = __pytraTuple_7[1];
          var nz = __pytraTuple_7[2];
          
          // Simple glass shading (reflection + refraction + light highlights).
          var __pytraTuple_8 = reflect(dx, dy, dz, nx, ny, nz);
          var rdx = __pytraTuple_8[0];
          var rdy = __pytraTuple_8[1];
          var rdz = __pytraTuple_8[2];
          var __pytraTuple_9 = refract(dx, dy, dz, nx, ny, nz, (1.0 / 1.45));
          var tdx = __pytraTuple_9[0];
          var tdy = __pytraTuple_9[1];
          var tdz = __pytraTuple_9[2];
          var __pytraTuple_10 = sky_color(rdx, rdy, rdz, tphase);
          var sr = __pytraTuple_10[0];
          var sg = __pytraTuple_10[1];
          var sb = __pytraTuple_10[2];
          var __pytraTuple_11 = sky_color(tdx, tdy, tdz, (tphase + 0.8));
          var tr = __pytraTuple_11[0];
          var tg = __pytraTuple_11[1];
          var tb = __pytraTuple_11[2];
          dynamic cosi = (((-(((dx * nx) + (dy * ny)) + (dz * nz)))) > (0.0) ? ((-(((dx * nx) + (dy * ny)) + (dz * nz)))) : (0.0));
          double fr = schlick(cosi, 0.04);
          r = ((tr * (1.0 - fr)) + (sr * fr));
          g = ((tg * (1.0 - fr)) + (sg * fr));
          b = ((tb * (1.0 - fr)) + (sb * fr));
          
          lxv = (lx - hx);
          lyv = (ly - hy);
          lzv = (lz - hz);
          var __pytraTuple_12 = normalize(lxv, lyv, lzv);
          ldx = __pytraTuple_12[0];
          ldy = __pytraTuple_12[1];
          ldz = __pytraTuple_12[2];
          ndotl = (((((nx * ldx) + (ny * ldy)) + (nz * ldz))) > (0.0) ? ((((nx * ldx) + (ny * ldy)) + (nz * ldz))) : (0.0));
          var __pytraTuple_13 = normalize((ldx - dx), (ldy - dy), (ldz - dz));
          var hvx = __pytraTuple_13[0];
          var hvy = __pytraTuple_13[1];
          var hvz = __pytraTuple_13[2];
          dynamic ndoth = (((((nx * hvx) + (ny * hvy)) + (nz * hvz))) > (0.0) ? ((((nx * hvx) + (ny * hvy)) + (nz * hvz))) : (0.0));
          dynamic spec = (ndoth * ndoth);
          spec = (spec * spec);
          spec = (spec * spec);
          spec = (spec * spec);
          glow = (10.0 / (((1.0 + (lxv * lxv)) + (lyv * lyv)) + (lzv * lzv)));
          r += (((0.2 * ndotl) + (0.8 * spec)) + (0.45 * glow));
          g += (((0.18 * ndotl) + (0.6 * spec)) + (0.35 * glow));
          b += (((0.26 * ndotl) + (1.0 * spec)) + (0.65 * glow));
          
          // Slight tint variation per sphere.
          if ((hit_kind == 2)) {
            r *= 0.95;
            g *= 1.05;
            b *= 1.1;
          } else {
            if ((hit_kind == 3)) {
              r *= 1.08;
              g *= 0.98;
              b *= 1.04;
            } else {
              r *= 1.02;
              g *= 1.1;
              b *= 0.95;
            }
          }
        }
      }
      // Slightly stronger tone mapping.
      r = math.sqrt(clamp01(r));
      g = math.sqrt(clamp01(g));
      b = math.sqrt(clamp01(b));
      frame[(row_base + px)] = quantize_332(r, g, b);
    }
  }
  return pytraBytes(frame);
}

void run_16_glass_sculpture_chaos() {
  int width = 320;
  int height = 240;
  int frames_n = 72;
  String out_path = "sample/out/16_glass_sculpture_chaos.gif";
  
  double start = perf_counter();
  var frames = [];
  for (var i = 0; i < frames_n; i++) {
    frames.add(render_frame(width, height, i, frames_n));
  }
  save_gif(out_path, width, height, frames, palette_332(), 6, 0);
  double elapsed = (perf_counter() - start);
  __pytraPrint(["output:", out_path]);
  __pytraPrint(["frames:", frames_n]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_16_glass_sculpture_chaos();
}
