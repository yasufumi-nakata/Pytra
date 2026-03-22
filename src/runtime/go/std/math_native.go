// Generated std/math.go delegates host bindings through this native seam.

package main

import "math"

func math_native_pi() float64    { return math.Pi }
func math_native_e() float64     { return math.E }
func math_native_sqrt(x any) float64  { return math.Sqrt(__pytra_float(x)) }
func math_native_sin(x any) float64   { return math.Sin(__pytra_float(x)) }
func math_native_cos(x any) float64   { return math.Cos(__pytra_float(x)) }
func math_native_tan(x any) float64   { return math.Tan(__pytra_float(x)) }
func math_native_exp(x any) float64   { return math.Exp(__pytra_float(x)) }
func math_native_log(x any) float64   { return math.Log(__pytra_float(x)) }
func math_native_log10(x any) float64 { return math.Log10(__pytra_float(x)) }
func math_native_fabs(x any) float64  { return math.Abs(__pytra_float(x)) }
func math_native_floor(x any) float64 { return math.Floor(__pytra_float(x)) }
func math_native_ceil(x any) float64  { return math.Ceil(__pytra_float(x)) }
func math_native_pow(x any, y any) float64 { return math.Pow(__pytra_float(x), __pytra_float(y)) }
