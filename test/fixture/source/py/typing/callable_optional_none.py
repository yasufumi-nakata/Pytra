from pytra.utils.assertions import py_assert_all, py_assert_eq


def inc(x: int) -> int:
    return x + 1


def run_callable_optional_none() -> bool:
    checks: list[bool] = []

    cb: callable[[int], int] | None = None
    checks.append(py_assert_eq(cb is None, True, "initial_none"))
    checks.append(py_assert_eq(cb is not None, False, "initial_not_none"))

    cb = inc
    checks.append(py_assert_eq(cb is None, False, "after_assign_none"))
    checks.append(py_assert_eq(cb is not None, True, "after_assign_not_none"))
    if cb is not None:
        checks.append(py_assert_eq(cb(4), 5, "invoke_after_guard"))

    return py_assert_all(checks, "callable_optional_none")


if __name__ == "__main__":
    print(run_callable_optional_none())
