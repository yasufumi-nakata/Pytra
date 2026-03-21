// Generated std/math.swift delegates host bindings through this native seam.

#if canImport(Darwin)
import Foundation
#else
import Glibc
#endif

func math_native_pi() -> Double { return Double.pi }
func math_native_e() -> Double { return 2.718281828459045 }
func math_native_sqrt(_ x: Double) -> Double { return sqrt(x) }
func math_native_sin(_ x: Double) -> Double { return sin(x) }
func math_native_cos(_ x: Double) -> Double { return cos(x) }
func math_native_tan(_ x: Double) -> Double { return tan(x) }
func math_native_exp(_ x: Double) -> Double { return exp(x) }
func math_native_log(_ x: Double) -> Double { return log(x) }
func math_native_log10(_ x: Double) -> Double { return log10(x) }
func math_native_fabs(_ x: Double) -> Double { return fabs(x) }
func math_native_floor(_ x: Double) -> Double { return floor(x) }
func math_native_ceil(_ x: Double) -> Double { return ceil(x) }
func math_native_pow(_ x: Double, _ y: Double) -> Double { return pow(x, y) }
