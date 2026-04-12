from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_set_update() -> bool:
    checks: list[bool] = []

    # update from list
    s: set[int] = {1, 2}
    s.update([3, 4, 5])
    checks.append(py_assert_eq(sorted(s), [1, 2, 3, 4, 5], "update_from_list"))

    # update with duplicates — no effect for existing elements
    s2: set[int] = {1, 2, 3}
    s2.update([2, 3, 4])
    checks.append(py_assert_eq(sorted(s2), [1, 2, 3, 4], "update_with_overlap"))

    # update from another set
    s3: set[str] = {"a", "b"}
    s3.update({"c", "d"})
    checks.append(py_assert_eq(sorted(s3), ["a", "b", "c", "d"], "update_from_set"))

    # update with empty
    s4: set[int] = {1, 2}
    s4.update([])
    checks.append(py_assert_eq(sorted(s4), [1, 2], "update_empty"))

    # update on empty set
    s5: set[int] = set()
    s5.update([10, 20])
    checks.append(py_assert_eq(sorted(s5), [10, 20], "update_on_empty"))

    return py_assert_all(checks, "set_update")


if __name__ == "__main__":
    print(run_set_update())
