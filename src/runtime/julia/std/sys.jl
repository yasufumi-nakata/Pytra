argv = Any[PROGRAM_FILE; ARGS]
path = Any[]

mutable struct __PytraSysModule
end

function set_argv(v)
    global argv = collect(v)
    return nothing
end

function set_path(v)
    global path = collect(v)
    return nothing
end

function Base.getproperty(::__PytraSysModule, name::Symbol)
    if name === :argv
        return argv
    end
    if name === :path
        return path
    end
    if name === :set_argv
        return set_argv
    end
    if name === :set_path
        return set_path
    end
    return getfield(__PytraSysModule(), name)
end

const sys = __PytraSysModule()
