from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_sorted_set() -> bool:
    checks: list[bool] = []

    # sorted(set) returns a sorted list
    s: set[int] = {5, 3, 1, 4, 2}
    result: list[int] = sorted(s)
    checks.append(py_assert_eq(result, [1, 2, 3, 4, 5], "sorted_int_set"))

    # sorted(set) of strings
    words: set[str] = {"cherry", "apple", "banana"}
    sorted_words: list[str] = sorted(words)
    checks.append(py_assert_eq(sorted_words, ["apple", "banana", "cherry"], "sorted_str_set"))

    # sorted empty set
    empty: set[int] = set()
    checks.append(py_assert_eq(sorted(empty), [], "sorted_empty_set"))

    # sorted(set) does not modify original
    s2: set[int] = {9, 7, 8}
    result2: list[int] = sorted(s2)
    checks.append(py_assert_eq(len(s2), 3, "original_set_unchanged"))
    checks.append(py_assert_eq(result2, [7, 8, 9], "sorted_set_order"))

    # sorted(set) with duplicates removed by set
    from_list: set[int] = {3, 1, 2, 1, 3}
    checks.append(py_assert_eq(sorted(from_list), [1, 2, 3], "sorted_set_dedup"))

    return py_assert_all(checks, "sorted_set")


if __name__ == "__main__":
    print(run_sorted_set())
