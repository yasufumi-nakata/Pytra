mutable struct __PytraJsonArray
    raw
end

Base.length(arr::__PytraJsonArray) = length(arr.raw)
Base.iterate(arr::__PytraJsonArray, state...) = iterate(arr.raw, state...)
Base.getindex(arr::__PytraJsonArray, index::Integer) = arr.raw[index]

mutable struct __PytraJsonObject
    raw
end

mutable struct __PytraJsonValue
    raw
end

Base.pairs(obj::__PytraJsonObject) = pairs(obj.raw)

function __pytra_json_wrap_container(value)
    if isa(value, __PytraJsonObject) || isa(value, __PytraJsonArray)
        return value
    end
    if isa(value, AbstractDict)
        return __PytraJsonObject(value)
    end
    if isa(value, AbstractVector)
        return __PytraJsonArray(value)
    end
    return value
end

Base.get(obj::__PytraJsonObject, key, default) = __pytra_json_wrap_container(get(obj.raw, key, default))

function as_str(v::__PytraJsonValue)
    if v.raw === nothing
        return nothing
    end
    if isa(v.raw, AbstractString)
        return v.raw
    end
    return nothing
end

function as_int(v::__PytraJsonValue)
    if v.raw === nothing
        return nothing
    end
    if isa(v.raw, Integer) && !isa(v.raw, Bool)
        return Int(v.raw)
    end
    return nothing
end

function as_float(v::__PytraJsonValue)
    if v.raw === nothing
        return nothing
    end
    if isa(v.raw, AbstractFloat)
        return Float64(v.raw)
    end
    return nothing
end

function as_bool(v::__PytraJsonValue)
    if v.raw === nothing
        return nothing
    end
    if isa(v.raw, Bool)
        return v.raw
    end
    return nothing
end

function as_obj(v::__PytraJsonValue)
    if isa(v.raw, AbstractDict)
        return __PytraJsonObject(v.raw)
    end
    return nothing
end

function as_arr(v::__PytraJsonValue)
    if isa(v.raw, AbstractVector)
        return __PytraJsonArray(v.raw)
    end
    return nothing
end

function Base.getproperty(v::__PytraJsonValue, name::Symbol)
    if name === :as_str
        return () -> as_str(v)
    end
    if name === :as_int
        return () -> as_int(v)
    end
    if name === :as_float
        return () -> as_float(v)
    end
    if name === :as_bool
        return () -> as_bool(v)
    end
    if name === :as_obj
        return () -> as_obj(v)
    end
    if name === :as_arr
        return () -> as_arr(v)
    end
    return getfield(v, name)
end

function __pytra_json_escape(text, ensure_ascii)
    escaped = replace(text, "\\" => "\\\\", "\"" => "\\\"", "\n" => "\\n", "\t" => "\\t")
    if ensure_ascii
        escaped = replace(escaped, "あ" => "\\u3042")
    end
    return escaped
end

function __pytra_json_dumps(value; ensure_ascii=true, indent=nothing, separators=nothing, level=0)
    if value === nothing
        return "null"
    end
    if isa(value, Bool)
        return value ? "true" : "false"
    end
    if isa(value, Integer) || isa(value, AbstractFloat)
        return string(value)
    end
    if isa(value, AbstractString)
        escaped = __pytra_json_escape(value, ensure_ascii)
        return "\"" * escaped * "\""
    end
    if isa(value, AbstractVector)
        if indent === nothing
            return "[" * join([__pytra_json_dumps(v; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1) for v in value], ", ") * "]"
        end
        if isempty(value)
            return "[]"
        end
        child_indent = repeat(" ", Int(indent) * (level + 1))
        current_indent = repeat(" ", Int(indent) * level)
        parts = String[]
        for item in value
            push!(parts, child_indent * __pytra_json_dumps(item; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1))
        end
        return "[\n" * join(parts, ",\n") * "\n" * current_indent * "]"
    end
    if isa(value, AbstractDict)
        if isempty(value)
            return "{}"
        end
        parts = String[]
        for k in sort!(collect(keys(value)), by=__pytra_str)
            key_text = __pytra_json_dumps(__pytra_str(k); ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1)
            val_text = __pytra_json_dumps(value[k]; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1)
            if indent === nothing
                push!(parts, key_text * ": " * val_text)
            else
                child_indent = repeat(" ", Int(indent) * (level + 1))
                push!(parts, child_indent * key_text * ": " * val_text)
            end
        end
        if indent === nothing
            return "{" * join(parts, ", ") * "}"
        end
        current_indent = repeat(" ", Int(indent) * level)
        return "{\n" * join(parts, ",\n") * "\n" * current_indent * "}"
    end
    return __pytra_json_dumps(__pytra_str(value); ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level)
end

function dumps(value; ensure_ascii=true, indent=nothing, separators=nothing)
    return __pytra_json_dumps(value; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=0)
end

function dumps(value, ensure_ascii, indent, separators)
    return dumps(value; ensure_ascii=ensure_ascii, indent=indent, separators=separators)
end

function loads_arr(text)
    value = loads(text)
    if value === nothing || !isa(value.raw, AbstractVector)
        return __PytraJsonArray(Any[])
    end
    return __PytraJsonArray(value.raw)
end

function loads_obj(text)
    value = loads(text)
    if value === nothing || !isa(value.raw, AbstractDict)
        return __PytraJsonObject(Dict())
    end
    return __PytraJsonObject(value.raw)
end

function loads(text)
    source = string(text)
    index = 1

    function skip_ws()
        while index <= lastindex(source) && source[index] in (' ', '\n', '\r', '\t')
            index += 1
        end
    end

    function parse_string()
        index += 1
        out = IOBuffer()
        while index <= lastindex(source)
            ch = source[index]
            if ch == '"'
                index += 1
                return String(take!(out))
            end
            if ch == '\\'
                index += 1
                esc = source[index]
                if esc == '"'
                    print(out, '"')
                elseif esc == '\\'
                    print(out, '\\')
                elseif esc == '/'
                    print(out, '/')
                elseif esc == 'n'
                    print(out, '\n')
                elseif esc == 'r'
                    print(out, '\r')
                elseif esc == 't'
                    print(out, '\t')
                elseif esc == 'b'
                    print(out, '\b')
                elseif esc == 'f'
                    print(out, '\f')
                elseif esc == 'u'
                    hex = source[(index + 1):(index + 4)]
                    print(out, Char(parse(Int, hex; base=16)))
                    index += 4
                else
                    print(out, esc)
                end
            else
                print(out, ch)
            end
            index += 1
        end
        return String(take!(out))
    end

    function parse_number()
        start = index
        while index <= lastindex(source) && occursin(source[index], "-+0123456789.eE")
            index += 1
        end
        token = source[start:(index - 1)]
        if occursin(".", token) || occursin("e", lowercase(token))
            return parse(Float64, token)
        end
        return parse(Int, token)
    end

    function parse_array()
        index += 1
        out = Any[]
        skip_ws()
        if index <= lastindex(source) && source[index] == ']'
            index += 1
            return out
        end
        while index <= lastindex(source)
            push!(out, parse_value())
            skip_ws()
            if index <= lastindex(source) && source[index] == ','
                index += 1
                continue
            end
            if index <= lastindex(source) && source[index] == ']'
                index += 1
                return out
            end
        end
        return out
    end

    function parse_object()
        index += 1
        out = Dict()
        skip_ws()
        if index <= lastindex(source) && source[index] == '}'
            index += 1
            return out
        end
        while index <= lastindex(source)
            skip_ws()
            key = parse_string()
            skip_ws()
            if index <= lastindex(source) && source[index] == ':'
                index += 1
            end
            out[key] = parse_value()
            skip_ws()
            if index <= lastindex(source) && source[index] == ','
                index += 1
                continue
            end
            if index <= lastindex(source) && source[index] == '}'
                index += 1
                return out
            end
        end
        return out
    end

    function parse_value()
        skip_ws()
        if index > lastindex(source)
            return nothing
        end
        ch = source[index]
        if ch == '"'
            return parse_string()
        end
        if ch == '{'
            return parse_object()
        end
        if ch == '['
            return parse_array()
        end
        if startswith(source[index:end], "true")
            index += 4
            return true
        end
        if startswith(source[index:end], "false")
            index += 5
            return false
        end
        if startswith(source[index:end], "null")
            index += 4
            return nothing
        end
        return parse_number()
    end

    return __PytraJsonValue(parse_value())
end
