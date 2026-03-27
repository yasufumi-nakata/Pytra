# isinstance on POD types uses exact type match (no subtype hierarchy).
# int8/int16/int32/int64 etc. are distinct types even though
# their value ranges have inclusion relationships.

from pytra.utils.assertions import py_assert_stdout


def _case_main() -> None:
    x16: int16 = 1
    x8: int8 = 1
    x32: int32 = 1
    x64: int64 = 1

    # exact match: True
    print(isinstance(x16, int16))
    print(isinstance(x8, int8))
    print(isinstance(x32, int32))
    print(isinstance(x64, int64))

    # different integer types: False (no subtype hierarchy)
    print(isinstance(x16, int8))
    print(isinstance(x8, int16))
    print(isinstance(x16, int32))
    print(isinstance(x32, int16))

    # float types: exact match only
    f32: float32 = 1.0
    f64: float64 = 1.0
    print(isinstance(f64, float64))
    print(isinstance(f32, float32))
    print(isinstance(f64, float32))
    print(isinstance(f32, float64))

if __name__ == "__main__":
    print(py_assert_stdout([
        'True', 'True', 'True', 'True',
        'False', 'False', 'False', 'False',
        'True', 'True', 'False', 'False',
    ], _case_main))
