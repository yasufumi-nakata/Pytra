// math_native.go: @extern delegation for pytra.std.math + pytra.std.random.
// Hand-written native implementation.
package main

import (
	"math"
	"math/rand"
	"time"
)

func py_sqrt(x any) float64  { return math.Sqrt(_toF64(x)) }
func py_sin(x any) float64   { return math.Sin(_toF64(x)) }
func py_cos(x any) float64   { return math.Cos(_toF64(x)) }
func py_tan(x any) float64   { return math.Tan(_toF64(x)) }
func py_atan2(y, x any) float64 { return math.Atan2(_toF64(y), _toF64(x)) }
func py_floor(x any) float64 { return math.Floor(_toF64(x)) }
func py_ceil(x any) float64  { return math.Ceil(_toF64(x)) }
func py_pow(x, y any) float64 { return math.Pow(_toF64(x), _toF64(y)) }
func py_exp(x any) float64   { return math.Exp(_toF64(x)) }
func py_log(x any) float64   { return math.Log(_toF64(x)) }
func py_fabs(x any) float64  { return math.Abs(_toF64(x)) }
func py_pi() float64                 { return math.Pi }

var _pytra_rng = rand.New(rand.NewSource(time.Now().UnixNano()))

func py_random() float64         { return _pytra_rng.Float64() }
func py_randint(a, b int64) int64 { return a + _pytra_rng.Int63n(b-a+1) }
func py_seed(s int64)            { _pytra_rng = rand.New(rand.NewSource(s)) }
