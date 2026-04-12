from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_reversed_basic() -> bool:
    checks: list[bool] = []

    # reversed(list)
    nums: list[int] = [1, 2, 3, 4, 5]
    rev: list[int] = list(reversed(nums))
    checks.append(py_assert_eq(rev, [5, 4, 3, 2, 1], "reversed_list"))

    # original unchanged
    checks.append(py_assert_eq(nums, [1, 2, 3, 4, 5], "original_unchanged"))

    # reversed(range)
    rev_range: list[int] = list(reversed(range(5)))
    checks.append(py_assert_eq(rev_range, [4, 3, 2, 1, 0], "reversed_range"))

    # reversed(range with step)
    rev_range2: list[int] = list(reversed(range(0, 10, 2)))
    checks.append(py_assert_eq(rev_range2, [8, 6, 4, 2, 0], "reversed_range_step"))

    # for x in reversed(...)
    acc: list[str] = []
    words: list[str] = ["a", "b", "c"]
    for w in reversed(words):
        acc.append(w)
    checks.append(py_assert_eq(acc, ["c", "b", "a"], "for_reversed"))

    # reversed empty list
    empty: list[int] = []
    checks.append(py_assert_eq(list(reversed(empty)), [], "reversed_empty"))

    # reversed single element
    single: list[int] = [42]
    checks.append(py_assert_eq(list(reversed(single)), [42], "reversed_single"))

    return py_assert_all(checks, "reversed_basic")


if __name__ == "__main__":
    print(run_reversed_basic())
