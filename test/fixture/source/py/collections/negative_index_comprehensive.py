from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_negative_index_comprehensive() -> bool:
    # list
    nums: list[int] = [10, 20, 30, 40, 50]
    # str
    s: str = "hello"
    # bytes
    b: bytes = bytes([1, 2, 3, 4, 5])
    # bytearray
    ba: bytearray = bytearray([100, 200, 255])

    checks: list[bool] = []

    # list negative index
    checks.append(py_assert_eq(nums[-1], 50, "list[-1]"))
    checks.append(py_assert_eq(nums[-2], 40, "list[-2]"))
    checks.append(py_assert_eq(nums[-5], 10, "list[-5] first"))

    # str negative index
    checks.append(py_assert_eq(s[-1], "o", "str[-1]"))
    checks.append(py_assert_eq(s[-3], "l", "str[-3]"))
    checks.append(py_assert_eq(s[-5], "h", "str[-5] first"))

    # bytes negative index
    checks.append(py_assert_eq(b[-1], 5, "bytes[-1]"))
    checks.append(py_assert_eq(b[-5], 1, "bytes[-5] first"))

    # bytearray negative index
    checks.append(py_assert_eq(ba[-1], 255, "bytearray[-1]"))
    checks.append(py_assert_eq(ba[-3], 100, "bytearray[-3] first"))

    # negative index after mutation
    nums.append(60)
    checks.append(py_assert_eq(nums[-1], 60, "list[-1] after append"))
    checks.append(py_assert_eq(nums[-2], 50, "list[-2] after append"))

    return py_assert_all(checks, "negative_index_comprehensive")


if __name__ == "__main__":
    print(run_negative_index_comprehensive())
