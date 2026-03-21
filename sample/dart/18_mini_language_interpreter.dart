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

bool __pytraIsinstance(dynamic obj, dynamic classType) {
  if (obj == null) return false;
  // Dart runtime type check is handled via 'is' keyword at emit site
  return false;
}

// --- end runtime helpers ---

class Token {
  String kind;
  String text;
  int pos;
  int number_value;
  Token(this.kind, this.text, this.pos, this.number_value);
}

class ExprNode {
  String kind;
  int value;
  String name;
  String op;
  int left;
  int right;
  int kind_tag;
  int op_tag;
  ExprNode(this.kind, this.value, this.name, this.op, this.left, this.right, this.kind_tag, this.op_tag);
}

class StmtNode {
  String kind;
  String name;
  int expr_index;
  int kind_tag;
  StmtNode(this.kind, this.name, this.expr_index, this.kind_tag);
}

dynamic tokenize(dynamic lines) {
  var single_char_token_tags = {"+": 1, "-": 2, "*": 3, "/": 4, "(": 5, ")": 6, "=": 7};
  var single_char_token_kinds = ["PLUS", "MINUS", "STAR", "SLASH", "LPAREN", "RPAREN", "EQUAL"];
  var tokens = [];
  for (var __it_1 in (lines).asMap().entries.map((e) => [e.key, e.value]).toList()) {
    var line_index = __it_1[0];
    var source = __it_1[1];
    int i = 0;
    int n = (source).length;
    while ((i < n)) {
      String ch = source[(i) < 0 ? source.length + (i) : (i)];
      
      if ((ch == " ")) {
        i = ((i + 1) as int);
        continue;
      }
      int single_tag = (single_char_token_tags[ch] ?? 0);
      if ((single_tag > 0)) {
        tokens.add(Token(single_char_token_kinds[((single_tag - 1)) < 0 ? single_char_token_kinds.length + ((single_tag - 1)) : ((single_tag - 1))], ch, i, 0));
        i = ((i + 1) as int);
        continue;
      }
      int start;
      String text;
      if (__pytraStrIsdigit(ch)) {
        int start = i;
        while (((i < n) && __pytraStrIsdigit(source[(i) < 0 ? source.length + (i) : (i)]))) {
          i = ((i + 1) as int);
        }
        String text = pytraStrSlice(source, start, i);
        tokens.add(Token("NUMBER", text, start, pytraInt(text)));
        continue;
      }
      if ((__pytraStrIsalpha(ch) || (ch == "_"))) {
        start = i;
        while (((i < n) && ((__pytraStrIsalpha(source[(i) < 0 ? source.length + (i) : (i)]) || (source[(i) < 0 ? source.length + (i) : (i)] == "_")) || __pytraStrIsdigit(source[(i) < 0 ? source.length + (i) : (i)])))) {
          i = ((i + 1) as int);
        }
        text = pytraStrSlice(source, start, i);
        if ((text == "let")) {
          tokens.add(Token("LET", text, start, 0));
        } else {
          if ((text == "print")) {
            tokens.add(Token("PRINT", text, start, 0));
          } else {
            tokens.add(Token("IDENT", text, start, 0));
          }
        }
        continue;
      }
      throw Exception(((((("tokenize error at line=" + (line_index).toString()) + " pos=") + (i).toString()) + " ch=") + ch));
    }
    tokens.add(Token("NEWLINE", "", n, 0));
  }
  tokens.add(Token("EOF", "", (lines).length, 0));
  return tokens;
}

class Parser {
  dynamic tokens;
  dynamic pos;
  dynamic expr_nodes;
  dynamic new_expr_nodes() {
    return [];
  }
  
  Parser(dynamic tokens) {
    this.tokens = tokens;
    this.pos = 0;
    this.expr_nodes = this.new_expr_nodes();
  }
  
  Token current_token() {
    return this.tokens[(this.pos) < 0 ? this.tokens.length + (this.pos) : (this.pos)];
  }
  
  Token previous_token() {
    return this.tokens[((this.pos - 1)) < 0 ? this.tokens.length + ((this.pos - 1)) : ((this.pos - 1))];
  }
  
  String peek_kind() {
    return this.current_token().kind;
  }
  
  bool match(String kind) {
    if ((this.peek_kind() == kind)) {
      this.pos = ((this.pos + 1) as int);
      return true;
    }
    return false;
  }
  
  Token expect(String kind) {
    Token token = this.current_token();
    if ((token.kind != kind)) {
      throw Exception(((((("parse error at pos=" + (token.pos).toString()) + ", expected=") + kind) + ", got=") + token.kind));
    }
    this.pos = ((this.pos + 1) as int);
    return token;
  }
  
  void skip_newlines() {
    while (this.match("NEWLINE")) {
      /* pass */
    }
  }
  
  int add_expr(ExprNode node) {
    this.expr_nodes.add(node);
    return ((this.expr_nodes).length - 1);
  }
  
  dynamic parse_program() {
    var stmts = [];
    this.skip_newlines();
    while ((this.peek_kind() != "EOF")) {
      StmtNode stmt = this.parse_stmt();
      stmts.add(stmt);
      this.skip_newlines();
    }
    return stmts;
  }
  
  StmtNode parse_stmt() {
    if (this.match("LET")) {
      String let_name = this.expect("IDENT").text;
      this.expect("EQUAL");
      int let_expr_index = this.parse_expr();
      return StmtNode("let", let_name, let_expr_index, 1);
    }
    if (this.match("PRINT")) {
      int print_expr_index = this.parse_expr();
      return StmtNode("print", "", print_expr_index, 3);
    }
    String assign_name = this.expect("IDENT").text;
    this.expect("EQUAL");
    int assign_expr_index = this.parse_expr();
    return StmtNode("assign", assign_name, assign_expr_index, 2);
  }
  
  int parse_expr() {
    return this.parse_add();
  }
  
  int parse_add() {
    int left = this.parse_mul();
    while (true) {
      int right;
      if (this.match("PLUS")) {
        int right = this.parse_mul();
        left = this.add_expr(ExprNode("bin", 0, "", "+", left, right, 3, 1));
        continue;
      }
      if (this.match("MINUS")) {
        right = this.parse_mul();
        left = this.add_expr(ExprNode("bin", 0, "", "-", left, right, 3, 2));
        continue;
      }
      break;
    }
    return left;
  }
  
  int parse_mul() {
    int left = this.parse_unary();
    while (true) {
      int right;
      if (this.match("STAR")) {
        int right = this.parse_unary();
        left = this.add_expr(ExprNode("bin", 0, "", "*", left, right, 3, 3));
        continue;
      }
      if (this.match("SLASH")) {
        right = this.parse_unary();
        left = this.add_expr(ExprNode("bin", 0, "", "/", left, right, 3, 4));
        continue;
      }
      break;
    }
    return left;
  }
  
  int parse_unary() {
    if (this.match("MINUS")) {
      int child = this.parse_unary();
      return this.add_expr(ExprNode("neg", 0, "", "", child, (-1), 4, 0));
    }
    return this.parse_primary();
  }
  
  int parse_primary() {
    if (this.match("NUMBER")) {
      Token token_num = this.previous_token();
      return this.add_expr(ExprNode("lit", token_num.number_value, "", "", (-1), (-1), 1, 0));
    }
    if (this.match("IDENT")) {
      Token token_ident = this.previous_token();
      return this.add_expr(ExprNode("var", 0, token_ident.text, "", (-1), (-1), 2, 0));
    }
    if (this.match("LPAREN")) {
      int expr_index = this.parse_expr();
      this.expect("RPAREN");
      return expr_index;
    }
    Token t = this.current_token();
    throw Exception(((("primary parse error at pos=" + (t.pos).toString()) + " got=") + t.kind));
  }
  
}

int eval_expr(int expr_index, dynamic expr_nodes, dynamic env) {
  ExprNode node = expr_nodes[(expr_index) < 0 ? expr_nodes.length + (expr_index) : (expr_index)];
  
  if ((node.kind_tag == 1)) {
    return node.value;
  }
  if ((node.kind_tag == 2)) {
    if ((!__pytraContains(env, node.name))) {
      throw Exception(("undefined variable: " + node.name));
    }
    return env[(node.name) < 0 ? env.length + (node.name) : (node.name)];
  }
  if ((node.kind_tag == 4)) {
    return (-eval_expr(node.left, expr_nodes, env));
  }
  if ((node.kind_tag == 3)) {
    int lhs = eval_expr(node.left, expr_nodes, env);
    int rhs = eval_expr(node.right, expr_nodes, env);
    if ((node.op_tag == 1)) {
      return (lhs + rhs);
    }
    if ((node.op_tag == 2)) {
      return (lhs - rhs);
    }
    if ((node.op_tag == 3)) {
      return (lhs * rhs);
    }
    if ((node.op_tag == 4)) {
      if ((rhs == 0)) {
        throw Exception("division by zero");
      }
      return (lhs ~/ rhs);
    }
    throw Exception(("unknown operator: " + node.op));
  }
  throw Exception(("unknown node kind: " + node.kind));
}

int execute(dynamic stmts, dynamic expr_nodes, bool trace) {
  var env = {};
  int checksum = 0;
  int printed = 0;
  
  for (var stmt in stmts) {
    if ((stmt.kind_tag == 1)) {
      env[stmt.name] = eval_expr(stmt.expr_index, expr_nodes, env);
      continue;
    }
    if ((stmt.kind_tag == 2)) {
      if ((!__pytraContains(env, stmt.name))) {
        throw Exception(("assign to undefined variable: " + stmt.name));
      }
      env[stmt.name] = eval_expr(stmt.expr_index, expr_nodes, env);
      continue;
    }
    int value = eval_expr(stmt.expr_index, expr_nodes, env);
    if (trace) {
      __pytraPrint([value]);
    }
    int norm = (value % 1000000007);
    if ((norm < 0)) {
      norm = ((norm + 1000000007) as int);
    }
    checksum = (((checksum * 131) + norm) % 1000000007);
    printed = ((printed + 1) as int);
  }
  if (trace) {
    __pytraPrint(["printed:", printed]);
  }
  return checksum;
}

dynamic build_benchmark_source(int var_count, int loops) {
  var lines = [];
  
  // Declare initial variables.
  for (var i = 0; i < var_count; i++) {
    lines.add(((("let v" + (i).toString()) + " = ") + ((i + 1)).toString()));
  }
  // Force evaluation of many arithmetic expressions.
  for (var i = 0; i < loops; i++) {
    int x = (i % var_count);
    int y = ((i + 3) % var_count);
    int c1 = ((i % 7) + 1);
    int c2 = ((i % 11) + 2);
    lines.add(((((((((("v" + (x).toString()) + " = (v") + (x).toString()) + " * ") + (c1).toString()) + " + v") + (y).toString()) + " + 10000) / ") + (c2).toString()));
    if (((i % 97) == 0)) {
      lines.add(("print v" + (x).toString()));
    }
  }
  // Print final values together.
  lines.add("print (v0 + v1 + v2 + v3)");
  return lines;
}

void run_demo() {
  var demo_lines = [];
  demo_lines.add("let a = 10");
  demo_lines.add("let b = 3");
  demo_lines.add("a = (a + b) * 2");
  demo_lines.add("print a");
  demo_lines.add("print a / b");
  
  var tokens = tokenize(demo_lines);
  Parser parser = Parser(tokens);
  var stmts = parser.parse_program();
  int checksum = execute(stmts, parser.expr_nodes, true);
  __pytraPrint(["demo_checksum:", checksum]);
}

void run_benchmark() {
  var source_lines = build_benchmark_source(32, 120000);
  double start = perf_counter();
  var tokens = tokenize(source_lines);
  Parser parser = Parser(tokens);
  var stmts = parser.parse_program();
  int checksum = execute(stmts, parser.expr_nodes, false);
  double elapsed = (perf_counter() - start);
  
  __pytraPrint(["token_count:", (tokens).length]);
  __pytraPrint(["expr_count:", (parser.expr_nodes).length]);
  __pytraPrint(["stmt_count:", (stmts).length]);
  __pytraPrint(["checksum:", checksum]);
  __pytraPrint(["elapsed_sec:", elapsed]);
}

void __pytra_main() {
  run_demo();
  run_benchmark();
}


void main() {
  __pytra_main();
}
