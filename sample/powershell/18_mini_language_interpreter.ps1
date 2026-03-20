#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

import { PYTRA_TYPE_ID, PY_TYPE_MAP, PY_TYPE_OBJECT, pyRegisterClassType, pyLen, pyStr } from "./runtime/js/native/built_in/py_runtime.js"
import { perf_counter } from "./runtime/js/generated/std/time.js"

class Token {
    static PYTRA_TYPE_ID = pyRegisterClassType [PY_TYPE_OBJECT]

    constructor kind text pos number_value {
    this[PYTRA_TYPE_ID] = Token.PYTRA_TYPE_ID
    this.kind = kind
    this.text = text
    this.pos = pos
    this.number_value = number_value
    }
}

class ExprNode {
    static PYTRA_TYPE_ID = pyRegisterClassType [PY_TYPE_OBJECT]

    constructor kind value name op left right kind_tag op_tag {
    this[PYTRA_TYPE_ID] = ExprNode.PYTRA_TYPE_ID
    this.kind = kind
    this.value = value
    this.name = name
    this.op = op
    this.left = left
    this.right = right
    this.kind_tag = kind_tag
    this.op_tag = op_tag
    }
}

class StmtNode {
    static PYTRA_TYPE_ID = pyRegisterClassType [PY_TYPE_OBJECT]

    constructor kind name expr_index kind_tag {
    this[PYTRA_TYPE_ID] = StmtNode.PYTRA_TYPE_ID
    this.kind = kind
    this.name = name
    this.expr_index = expr_index
    this.kind_tag = kind_tag
    }
}

function tokenize {
    param($lines)
    $single_char_token_tags = ({[$PYTRA_TYPE_ID]: $PY_TYPE_MAP, "+": 1, "-": 2, "*": 3, "/": 4, "(": 5, ")": 6, "=": 7})
    $single_char_token_kinds = @("PLUS", "MINUS", "STAR", "SLASH", "LPAREN", "RPAREN", "EQUAL")
    $tokens = @()
    for ($const [$line_index, $source] $of $lines.map(($__v, __i) = -$gt  [$__i, $__v])) {
        $i = 0
        $n = (source).Length
        while ($i  -$lt  $n) {
            $ch = $source[(((i)  -$lt  0) ? ((source).Length + (i)) : (i))]

            if ($ch -$eq " ") {
                i += 1
                continue
            }
            $single_tag = ($Object.prototype.hasOwnProperty.call($single_char_token_tags, ch) ? $single_char_token_tags[$ch] : 0)
            if ($single_tag  -$gt  0) {
                tokens.push(new Token single_char_token_kinds[(((single_tag - 1  -lt  0) ? ((single_char_token_kinds).Length + (single_tag - 1)) : (single_tag - 1))], ch, i, 0))
                i += 1
                continue
            }
            if (($typeof $ch -$eq "string") -$and $ch.Length  -$gt  0 -$and /^[0-9]+$/.test(ch)) {
                $start = $i
                while ($i  -$lt  $n -and ($typeof $source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))] -$eq "string") -$and $source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))]).Length  -$gt  0 -$and /^[0-9]+$/.test($source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))])))) {
                    i += 1
                }
                $text = $source.slice($start, i)
                tokens.push(new Token "NUMBER" text start Math.trunc(Number(text)))
                continue
            }
            if ((($typeof $ch -$eq "string") -$and $ch.Length  -$gt  0 -$and /^[$A-$Za-$z]+$/.test(ch)) -$or $ch -$eq "_") {
                $start = $i
                while ($i  -$lt  $n -and ($typeof $source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))] -$eq "string") -$and $source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))]).Length  -$gt  0 -$and /^[$A-$Za-$z]+$/.test($source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))]))) -$or $source[(((i)  -$lt  0) ? ((source).Length + (i)) : (i))] -$eq "_" -or ($typeof $source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))] -$eq "string") -$and $source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))]).Length  -$gt  0 -$and /^[0-9]+$/.test($source[((($i  -$lt  0) ? ((source).Length + (i)) : (i))])))) {
                    i += 1
                }
                $text = $source.slice($start, i)
                if ($text -$eq "let") {
                    tokens.push(new Token "LET" text start 0)
                } else {
                    if ($text -$eq "print") {
                        tokens.push(new Token "PRINT" text start 0)
                    } else {
                        tokens.push(new Token "IDENT" text start 0)
                    }
                }
                continue
            }
            throw "tokenize error at line=" + __pytra_str line_index + " pos=" + __pytra_str i + " ch=" + ch
        }
        tokens.push(new Token "NEWLINE" "" n 0)
    }
    tokens.push(new Token "EOF" "" (lines.Length, 0))
    return $tokens
}

class Parser {
    static PYTRA_TYPE_ID = pyRegisterClassType [PY_TYPE_OBJECT]

    constructor tokens {
        this.tokens = (Array.isArray(tokens) ? tokens.slice() : Array.from(tokens))
        this.pos = 0
        this.expr_nodes = this.new_expr_nodes()
    this[PYTRA_TYPE_ID] = Parser.PYTRA_TYPE_ID
    }

    new_expr_nodes {
        return []
    }

    current_token {
        return this.tokens[(((this.pos)  -$lt  0) ? ((this.tokens).Length + (this.pos)) : (this.pos))]
    }

    previous_token {
        return this.tokens[(((this.pos - 1)  -$lt  0) ? ((this.tokens).Length + (this.pos - 1)) : (this.pos - 1))]
    }

    peek_kind {
        return this.current_token().kind
    }

    match kind {
        if (this.peek_kind() -$eq $kind) {
            this.pos += 1
            return $$true
        }
        return $$false
    }

    expect kind {
        $token = this.current_token()
        if ($token.kind -$ne $kind) {
            throw "parse error at pos=" + pyStr token.pos + ", expected=" + kind + ", got=" + token.kind
        }
        this.pos += 1
        return $token
    }

    skip_newlines {
        while (this.match("NEWLINE")) {
            
        }
    }

    add_expr node {
        this.expr_nodes.push(node)
        return (this.expr_nodes).Length - 1
    }

    parse_program {
        $stmts = @()
        this.skip_newlines()
        while (this.peek_kind() -$ne "EOF") {
            $stmt = this.parse_stmt()
            stmts.push(stmt)
            this.skip_newlines()
        }
        return $stmts
    }

    parse_stmt {
        if (this.match("LET")) {
            $let_name = this.expect("IDENT").text
            this.expect("EQUAL")
            $let_expr_index = this.parse_expr()
            return $StmtNode "let" $let_name $let_expr_index 1
        }
        if (this.match("PRINT")) {
            $print_expr_index = this.parse_expr()
            return $StmtNode "print" "" $print_expr_index 3
        }
        $assign_name = this.expect("IDENT").text
        this.expect("EQUAL")
        $assign_expr_index = this.parse_expr()
        return $StmtNode "assign" $assign_name $assign_expr_index 2
    }

    parse_expr {
        return this.parse_add()
    }

    parse_add {
        $left = this.parse_mul()
        while ($true) {
            if (this.match("PLUS")) {
                $right = this.parse_mul()
                left = this.add_expr(new ExprNode "bin" 0 "" "+" left right 3 1)
                continue
            }
            if (this.match("MINUS")) {
                $right = this.parse_mul()
                left = this.add_expr(new ExprNode "bin" 0 "" "-" left right 3 2)
                continue
            }
            break
        }
        return $left
    }

    parse_mul {
        $left = this.parse_unary()
        while ($true) {
            if (this.match("STAR")) {
                $right = this.parse_unary()
                left = this.add_expr(new ExprNode "bin" 0 "" "*" left right 3 3)
                continue
            }
            if (this.match("SLASH")) {
                $right = this.parse_unary()
                left = this.add_expr(new ExprNode "bin" 0 "" "/" left right 3 4)
                continue
            }
            break
        }
        return $left
    }

    parse_unary {
        if (this.match("MINUS")) {
            $child = this.parse_unary()
            return this.add_expr($ExprNode "neg" 0 "" "" $child -1 4 0)
        }
        return this.parse_primary()
    }

    parse_primary {
        if (this.match("NUMBER")) {
            $token_num = this.previous_token()
            return this.add_expr($ExprNode "lit" $token_num.number_value "" "" -1 -1 1 0)
        }
        if (this.match("IDENT")) {
            $token_ident = this.previous_token()
            return this.add_expr($ExprNode "var" 0 $token_ident.text "" -1 -1 2 0)
        }
        if (this.match("LPAREN")) {
            $expr_index = this.parse_expr()
            this.expect("RPAREN")
            return $expr_index
        }
        $t = this.current_token()
        throw "primary parse error at pos=" + pyStr t.pos + " got=" + t.kind
    }
}

function eval_expr {
    param($expr_index, $expr_nodes, $env)
    $node = $expr_nodes[(((expr_index)  -$lt  0) ? ((expr_nodes).Length + (expr_index)) : (expr_index))]

    if ($node.kind_tag -$eq 1) {
        return $node.value
    }
    if ($node.kind_tag -$eq 2) {
        if (-$not $Object.prototype.hasOwnProperty.call($env, $node.name)) {
            throw "$null variable: " + node.name
        }
        return $env[$node.name]
    }
    if ($node.kind_tag -$eq 4) {
        return -$eval_expr $node.left $expr_nodes $env
    }
    if ($node.kind_tag -$eq 3) {
        $lhs = $eval_expr $node.left $expr_nodes $env
        $rhs = $eval_expr $node.right $expr_nodes $env
        if ($node.op_tag -$eq 1) {
            return $lhs + $rhs
        }
        if ($node.op_tag -$eq 2) {
            return $lhs - $rhs
        }
        if ($node.op_tag -$eq 3) {
            return $lhs * $rhs
        }
        if ($node.op_tag -$eq 4) {
            if ($rhs -$eq 0) {
                throw "division by zero"
            }
            return [Math]::$Floor $lhs / $rhs
        }
        throw "unknown operator: " + node.op
    }
    throw "unknown node kind: " + node.kind
}

function execute {
    param($stmts, $expr_nodes, $trace)
    $env = ({[$PYTRA_TYPE_ID]: $PY_TYPE_MAP})
    $checksum = 0
    $printed = 0

    foreach ($stmt in $stmts) {
        if ($stmt.kind_tag -$eq 1) {
            env[stmt.name] = eval_expr stmt.expr_index expr_nodes env
            continue
        }
        if ($stmt.kind_tag -$eq 2) {
            if (-$not $Object.prototype.hasOwnProperty.call($env, $stmt.name)) {
                throw "assign to $null variable: " + stmt.name
            }
            env[stmt.name] = eval_expr stmt.expr_index expr_nodes env
            continue
        }
        $value = $eval_expr $stmt.expr_index $expr_nodes $env
        if ($trace) {
            __pytra_print value
        }
        $norm = $value % 1000000007
        if ($norm  -$lt  0) {
            norm += 1000000007
        }
        checksum = (checksum * 131 + norm) % 1000000007
        printed += 1
    }
    if ($trace) {
        __pytra_print "printed:" printed
    }
    return $checksum
}

function build_benchmark_source {
    param($var_count, $loops)
    $lines = @()

    // Declare initial variables.
    for ($i = 0; $i  -$lt  $var_count; $i += 1) {
        lines.push("let v" + __pytra_str i + " = " + __pytra_str i + 1)
    }
    // Force evaluation of many arithmetic expressions.
    for ($i = 0; $i  -$lt  $loops; $i += 1) {
        $x = $i % $var_count
        $y = ($i + 3) % $var_count
        $c1 = $i % 7 + 1
        $c2 = $i % 11 + 2
        lines.push("v" + __pytra_str x + " = (v" + __pytra_str x + " * " + __pytra_str c1 + " + v" + __pytra_str y + " + 10000) / " + __pytra_str c2)
        if ($i % 97 -$eq 0) {
            lines.push("print v" + __pytra_str x)
        }
    }
    // Print final values together.
    lines.push("__pytra_print v0 + v1 + v2 + v3")
    return $lines
}

function run_demo {
    param()
    $demo_lines = @()
    demo_lines.push("let a = 10")
    demo_lines.push("let b = 3")
    demo_lines.push("a = (a + b) * 2")
    demo_lines.push("print a")
    demo_lines.push("print a / b")

    $tokens = $tokenize $demo_lines
    $parser = $Parser $tokens
    $stmts = $parser.parse_program()
    $checksum = $execute $stmts $parser.expr_nodes $true
    __pytra_print "demo_checksum:" checksum
}

function run_benchmark {
    param()
    $source_lines = $build_benchmark_source 32 120000
    $start = $perf_counter
    $tokens = $tokenize $source_lines
    $parser = $Parser $tokens
    $stmts = $parser.parse_program()
    $checksum = $execute $stmts $parser.expr_nodes $false
    $elapsed = $perf_counter - $start

    __pytra_print "token_count:" (tokens).Length
    __pytra_print "expr_count:" pyLen parser.expr_nodes
    __pytra_print "stmt_count:" (stmts).Length
    __pytra_print "checksum:" checksum
    __pytra_print "elapsed_sec:" elapsed
}

function __pytra_main {
    param()
    run_demo
    run_benchmark
}

__pytra_main

if (Get-Command -Name main -ErrorAction SilentlyContinue) {
    main
}
