from pytra.utils.assertions import py_assert_all, py_assert_eq


def check_dict_narrowing(x: int | dict[str, int]) -> list[bool]:
    checks: list[bool] = []
    if isinstance(x, dict):
        # x should be narrowed to dict[str, int], not bare dict
        val: int = x["key"]
        checks.append(py_assert_eq(val, 42, "dict_narrowed_access"))
        # append to typed list — should not trigger covariant copy
        results: list[dict[str, int]] = []
        results.append(x)
        checks.append(py_assert_eq(len(results), 1, "dict_narrowed_append"))
        checks.append(py_assert_eq(results[0]["key"], 42, "dict_narrowed_list_access"))
    else:
        checks.append(py_assert_eq(x, 99, "int_branch"))
    return checks


def check_list_narrowing(y: str | list[int] | None) -> list[bool]:
    checks: list[bool] = []
    if isinstance(y, list):
        # y should be narrowed to list[int]
        first: int = y[0]
        checks.append(py_assert_eq(first, 10, "list_narrowed_access"))
        total: int = 0
        for v in y:
            total += v
        checks.append(py_assert_eq(total, 60, "list_narrowed_sum"))
    elif isinstance(y, str):
        checks.append(py_assert_eq(y, "hello", "str_branch"))
    else:
        checks.append(py_assert_eq(y is None, True, "none_branch"))
    return checks


def run_isinstance_union_narrowing() -> bool:
    checks: list[bool] = []

    # dict narrowing from union
    d: dict[str, int] = {"key": 42}
    checks.extend(check_dict_narrowing(d))
    checks.extend(check_dict_narrowing(99))

    # list narrowing from union
    nums: list[int] = [10, 20, 30]
    checks.extend(check_list_narrowing(nums))
    checks.extend(check_list_narrowing("hello"))
    checks.extend(check_list_narrowing(None))

    return py_assert_all(checks, "isinstance_union_narrowing")


if __name__ == "__main__":
    print(run_isinstance_union_narrowing())
