include(joinpath(@__DIR__, "built_in", "py_runtime.jl"))

include(joinpath(@__DIR__, "std", "pathlib.jl"))
include(joinpath(@__DIR__, "std", "time.jl"))

mutable struct Token
    kind
    text
    pos
    number_value
end

mutable struct ExprNode
    kind
    value
    name
    op
    left
    right
    kind_tag
    op_tag
end

mutable struct StmtNode
    kind
    name
    expr_index
    kind_tag
end

function tokenize(lines)
    single_char_token_tags = Dict("+" => 1, "-" => 2, "*" => 3, "/" => 4, "(" => 5, ")" => 6, "=" => 7)
    single_char_token_kinds = ["PLUS", "MINUS", "STAR", "SLASH", "LPAREN", "RPAREN", "EQUAL"]
    tokens = Any[]
    __enum_idx_1 = 0
    for source in lines
        line_index = __enum_idx_1
        i = 0
        n = length(source)
        while (i < n)
            ch = string(source[__pytra_idx(i, length(source))])
            
            if (ch == " ")
                i = i + 1
                continue
            end
            single_tag = get(single_char_token_tags, ch, 0)
            if (single_tag > 0)
                push!(tokens, Token(single_char_token_kinds[__pytra_idx((single_tag - 1), length(single_char_token_kinds))], ch, i, 0))
                i = i + 1
                continue
            end
            start = nothing
            text = nothing
            if __pytra_str_isdigit(ch)
                start = i
                while ((i < n) && __pytra_str_isdigit(string(source[__pytra_idx(i, length(source))])))
                    i = i + 1
                end
                text = source[(start + 1):i]
                push!(tokens, Token("NUMBER", text, start, __pytra_int(text)))
                continue
            end
            if (__pytra_str_isalpha(ch) || (ch == "_"))
                start = i
                while ((i < n) && ((__pytra_str_isalpha(string(source[__pytra_idx(i, length(source))])) || (string(source[__pytra_idx(i, length(source))]) == "_")) || __pytra_str_isdigit(string(source[__pytra_idx(i, length(source))]))))
                    i = i + 1
                end
                text = source[(start + 1):i]
                if (text == "let")
                    push!(tokens, Token("LET", text, start, 0))
                elseif (text == "print")
                    push!(tokens, Token("PRINT", text, start, 0))
                else
                    push!(tokens, Token("IDENT", text, start, 0))
                end
                continue
            end
            error(((((("tokenize error at line=" * string(line_index)) * " pos=") * string(i)) * " ch=") * ch))
        end
        push!(tokens, Token("NEWLINE", "", n, 0))
        __enum_idx_1 = __enum_idx_1 + 1
    end
    push!(tokens, Token("EOF", "", length(lines), 0))
    return tokens
end

mutable struct Parser
    tokens
    pos
    expr_nodes
end

function new_expr_nodes(self::Parser)
    return Any[]
end

function Parser(tokens)
    self = Parser(nothing, nothing, nothing)
    self.tokens = tokens
    self.pos = 0
    self.expr_nodes = new_expr_nodes(self)
    return self
end

function current_token(self::Parser)
    return self.tokens[__pytra_idx(self.pos, length(self.tokens))]
end

function previous_token(self::Parser)
    return self.tokens[__pytra_idx((self.pos - 1), length(self.tokens))]
end

function peek_kind(self::Parser)
    return current_token(self).kind
end

function match(self::Parser, kind)
    if (peek_kind(self) == kind)
        self.pos = self.pos + 1
        return true
    end
    return false
end

function expect(self::Parser, kind)
    token = current_token(self)
    if (token.kind != kind)
        error(((((("parse error at pos=" * string(token.pos)) * ", expected=") * kind) * ", got=") * token.kind))
    end
    self.pos = self.pos + 1
    return token
end

function skip_newlines(self::Parser)
    while match(self, "NEWLINE")
    end
end

function add_expr(self::Parser, node)
    push!(self.expr_nodes, node)
    return (length(self.expr_nodes) - 1)
end

function parse_program(self::Parser)
    stmts = Any[]
    skip_newlines(self)
    while (peek_kind(self) != "EOF")
        stmt = parse_stmt(self)
        push!(stmts, stmt)
        skip_newlines(self)
    end
    return stmts
end

function parse_stmt(self::Parser)
    if match(self, "LET")
        let_name = expect(self, "IDENT").text
        expect(self, "EQUAL")
        let_expr_index = parse_expr(self)
        return StmtNode("let", let_name, let_expr_index, 1)
    end
    if match(self, "PRINT")
        print_expr_index = parse_expr(self)
        return StmtNode("print", "", print_expr_index, 3)
    end
    assign_name = expect(self, "IDENT").text
    expect(self, "EQUAL")
    assign_expr_index = parse_expr(self)
    return StmtNode("assign", assign_name, assign_expr_index, 2)
end

function parse_expr(self::Parser)
    return parse_add(self)
end

function parse_add(self::Parser)
    left = parse_mul(self)
    while true
        right = nothing
        if match(self, "PLUS")
            right = parse_mul(self)
            left = add_expr(self, ExprNode("bin", 0, "", "+", left, right, 3, 1))
            continue
        end
        if match(self, "MINUS")
            right = parse_mul(self)
            left = add_expr(self, ExprNode("bin", 0, "", "-", left, right, 3, 2))
            continue
        end
        break
    end
    return left
end

function parse_mul(self::Parser)
    left = parse_unary(self)
    while true
        right = nothing
        if match(self, "STAR")
            right = parse_unary(self)
            left = add_expr(self, ExprNode("bin", 0, "", "*", left, right, 3, 3))
            continue
        end
        if match(self, "SLASH")
            right = parse_unary(self)
            left = add_expr(self, ExprNode("bin", 0, "", "/", left, right, 3, 4))
            continue
        end
        break
    end
    return left
end

function parse_unary(self::Parser)
    if match(self, "MINUS")
        child = parse_unary(self)
        return add_expr(self, ExprNode("neg", 0, "", "", child, (-1), 4, 0))
    end
    return parse_primary(self)
end

function parse_primary(self::Parser)
    if match(self, "NUMBER")
        token_num = previous_token(self)
        return add_expr(self, ExprNode("lit", token_num.number_value, "", "", (-1), (-1), 1, 0))
    end
    if match(self, "IDENT")
        token_ident = previous_token(self)
        return add_expr(self, ExprNode("var", 0, token_ident.text, "", (-1), (-1), 2, 0))
    end
    if match(self, "LPAREN")
        expr_index = parse_expr(self)
        expect(self, "RPAREN")
        return expr_index
    end
    t = current_token(self)
    error(((("primary parse error at pos=" * string(t.pos)) * " got=") * t.kind))
end

function eval_expr(expr_index, expr_nodes, env)
    node = expr_nodes[__pytra_idx(expr_index, length(expr_nodes))]
    
    if (node.kind_tag == 1)
        return node.value
    end
    if (node.kind_tag == 2)
        if (!(__pytra_contains(env, node.name)))
            error(("undefined variable: " * node.name))
        end
        return env[node.name]
    end
    if (node.kind_tag == 4)
        return (-eval_expr(node.left, expr_nodes, env))
    end
    if (node.kind_tag == 3)
        lhs = eval_expr(node.left, expr_nodes, env)
        rhs = eval_expr(node.right, expr_nodes, env)
        if (node.op_tag == 1)
            return (lhs + rhs)
        end
        if (node.op_tag == 2)
            return (lhs - rhs)
        end
        if (node.op_tag == 3)
            return (lhs * rhs)
        end
        if (node.op_tag == 4)
            if (rhs == 0)
                error("division by zero")
            end
            return (lhs ÷ rhs)
        end
        error(("unknown operator: " * node.op))
    end
    error(("unknown node kind: " * node.kind))
end

function execute(stmts, expr_nodes, trace)
    env = Dict{Any,Any}()
    checksum = 0
    printed = 0
    
    for stmt in stmts
        if (stmt.kind_tag == 1)
            env[stmt.name] = eval_expr(stmt.expr_index, expr_nodes, env)
            continue
        end
        if (stmt.kind_tag == 2)
            if (!(__pytra_contains(env, stmt.name)))
                error(("assign to undefined variable: " * stmt.name))
            end
            env[stmt.name] = eval_expr(stmt.expr_index, expr_nodes, env)
            continue
        end
        value = eval_expr(stmt.expr_index, expr_nodes, env)
        if trace
            __pytra_print(value)
        end
        norm = (value % 1000000007)
        if (norm < 0)
            norm = norm + 1000000007
        end
        checksum = (((checksum * 131) + norm) % 1000000007)
        printed = printed + 1
    end
    if trace
        __pytra_print("printed:", printed)
    end
    return checksum
end

function build_benchmark_source(var_count, loops)
    lines = Any[]
    i = nothing
    
    # Declare initial variables.
    for i in 0:var_count - 1
        push!(lines, ((("let v" * string(i)) * " = ") * string((i + 1))))
    end
    # Force evaluation of many arithmetic expressions.
    for i in 0:loops - 1
        x = (i % var_count)
        y = ((i + 3) % var_count)
        c1 = ((i % 7) + 1)
        c2 = ((i % 11) + 2)
        push!(lines, ((((((((("v" * string(x)) * " = (v") * string(x)) * " * ") * string(c1)) * " + v") * string(y)) * " + 10000) / ") * string(c2)))
        if ((i % 97) == 0)
            push!(lines, ("print v" * string(x)))
        end
    end
    # Print final values together.
    push!(lines, "print (v0 + v1 + v2 + v3)")
    return lines
end

function run_demo()
    demo_lines = Any[]
    push!(demo_lines, "let a = 10")
    push!(demo_lines, "let b = 3")
    push!(demo_lines, "a = (a + b) * 2")
    push!(demo_lines, "print a")
    push!(demo_lines, "print a / b")
    
    tokens = tokenize(demo_lines)
    parser = Parser(tokens)
    stmts = parse_program(parser)
    checksum = execute(stmts, parser.expr_nodes, true)
    __pytra_print("demo_checksum:", checksum)
end

function run_benchmark()
    out_path = "sample/out/18_mini_language_interpreter.txt"
    source_lines = build_benchmark_source(32, 120000)
    start = perf_counter()
    tokens = tokenize(source_lines)
    parser = Parser(tokens)
    stmts = parse_program(parser)
    checksum = execute(stmts, parser.expr_nodes, false)
    elapsed = (perf_counter() - start)
    
    result = (((((((("token_count:" * string(length(tokens))) * "\nexpr_count:") * string(length(parser.expr_nodes))) * "\nstmt_count:") * string(length(stmts))) * "\nchecksum:") * string(checksum)) * "\n")
    p = Path(out_path)
    write_text(p, result, "utf-8")
    
    __pytra_print("token_count:", length(tokens))
    __pytra_print("expr_count:", length(parser.expr_nodes))
    __pytra_print("stmt_count:", length(stmts))
    __pytra_print("checksum:", checksum)
    __pytra_print("elapsed_sec:", elapsed)
end

function __pytra_main()
    run_demo();
    run_benchmark();
end


__pytra_main();
