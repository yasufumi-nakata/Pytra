-- Generated std/math.lua delegates host bindings through this native seam.
-- source: src/runtime/cs/std/math_native.cs (reference)

local math_native = {}

math_native.pi = math.pi
math_native.e = 2.718281828459045

function math_native.sqrt(x) return math.sqrt(tonumber(x) or 0) end
function math_native.sin(x) return math.sin(tonumber(x) or 0) end
function math_native.cos(x) return math.cos(tonumber(x) or 0) end
function math_native.tan(x) return math.tan(tonumber(x) or 0) end
function math_native.exp(x) return math.exp(tonumber(x) or 0) end
function math_native.log(x) return math.log(tonumber(x) or 0) end
function math_native.log10(x) return math.log(tonumber(x) or 0, 10) end
function math_native.fabs(x) return math.abs(tonumber(x) or 0) end
function math_native.floor(x) return math.floor(tonumber(x) or 0) end
function math_native.ceil(x) return math.ceil(tonumber(x) or 0) end
function math_native.pow(x, y) return (tonumber(x) or 0) ^ (tonumber(y) or 0) end

return math_native
