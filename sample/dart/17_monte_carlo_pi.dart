import 'py_runtime.dart';


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

// 17: Sample that scans a large grid using integer arithmetic only and computes a checksum.
// It avoids floating-point error effects, making cross-language comparisons easier.

int run_integer_grid_checksum(int width, int height, int seed) {
  int mod_main = 2147483647;
  int mod_out = 1000000007;
  int acc = (seed % mod_out);
  
  for (var y = 0; y < height; y++) {
    int row_sum = 0;
    for (var x = 0; x < width; x++) {
      int v = ((((x * 37) + (y * 73)) + seed) % mod_main);
      v = (((v * 48271) + 1) % mod_main);
      row_sum = ((row_sum + (v % 256)) as int);
    }
    acc = ((acc + (row_sum * (y + 1))) % mod_out);
  }
  return acc;
}

void run_integer_benchmark() {
  // Previous baseline: 2400 x 1600 (= 3,840,000 cells).
  // 7600 x 5000 (= 38,000,000 cells) is ~9.9x larger to make this case
  // meaningful in runtime benchmarks.
  int width = 7600;
  int height = 5000;
  
  double start = perf_counter();
  int checksum = run_integer_grid_checksum(width, height, 123456789);
  double elapsed = (perf_counter() - start);
  
  __pytraPrint(["pixels:", (width * height)]);
  __pytraPrint(["checksum:", checksum]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}


void main() {
  run_integer_benchmark();
}
