#ifndef PYTRA_BUILT_IN_PY_SCALAR_TYPES_H
#define PYTRA_BUILT_IN_PY_SCALAR_TYPES_H

#include <cstdint>

using int8 = ::std::int8_t;
using uint8 = ::std::uint8_t;
using int16 = ::std::int16_t;
using uint16 = ::std::uint16_t;
using int32 = ::std::int32_t;
using uint32 = ::std::uint32_t;
using int64 = ::std::int64_t;
using uint64 = ::std::uint64_t;
using float32 = float;
using float64 = double;

// tagged union / isinstance 判定に使用する型 ID。
using pytra_type_id = uint32;

// type_id は target 非依存で stable な型判定キーとして扱う。
// 予約領域（0-999）は runtime 組み込み型に割り当てる。
static constexpr pytra_type_id PYTRA_TID_NONE = 0;
static constexpr pytra_type_id PYTRA_TID_BOOL = 1;
static constexpr pytra_type_id PYTRA_TID_INT = 2;
static constexpr pytra_type_id PYTRA_TID_FLOAT = 3;
static constexpr pytra_type_id PYTRA_TID_STR = 4;
static constexpr pytra_type_id PYTRA_TID_LIST = 5;
static constexpr pytra_type_id PYTRA_TID_DICT = 6;
static constexpr pytra_type_id PYTRA_TID_SET = 7;
static constexpr pytra_type_id PYTRA_TID_OBJECT = 8;
static constexpr pytra_type_id PYTRA_TID_USER_BASE = 1000;

#endif  // PYTRA_BUILT_IN_PY_SCALAR_TYPES_H
