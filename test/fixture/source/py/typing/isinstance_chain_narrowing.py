from pytra.utils.assertions import py_assert_all, py_assert_eq


def check_chain(x: int | str | list[int] | None) -> list[bool]:
    checks: list[bool] = []

    if isinstance(x, int):
        # x narrowed to int
        doubled: int = x * 2
        checks.append(py_assert_eq(doubled, 20, "int_branch"))
    elif isinstance(x, str):
        # x narrowed to str (int excluded from union)
        upper: str = x.upper()
        checks.append(py_assert_eq(upper, "HELLO", "str_branch"))
    elif isinstance(x, list):
        # x narrowed to list[int] (int and str excluded)
        total: int = 0
        for v in x:
            total += v
        checks.append(py_assert_eq(total, 6, "list_branch"))
    else:
        # x narrowed to None (int, str, list[int] all excluded)
        checks.append(py_assert_eq(x is None, True, "none_branch"))

    return checks


def check_two_member(y: str | int) -> list[bool]:
    checks: list[bool] = []

    if isinstance(y, str):
        # y narrowed to str
        checks.append(py_assert_eq(y.startswith("ab"), True, "str_startswith"))
    else:
        # y narrowed to int (str excluded, only int remains)
        remainder: int = y % 3
        checks.append(py_assert_eq(remainder, 1, "int_modulo"))

    return checks


def check_assign_after_narrow(z: int | str | None) -> list[bool]:
    checks: list[bool] = []

    if isinstance(z, int):
        n: int = z
        checks.append(py_assert_eq(n + 1, 43, "assign_int"))
    elif isinstance(z, str):
        s: str = z
        checks.append(py_assert_eq(len(s), 3, "assign_str"))
    else:
        checks.append(py_assert_eq(z is None, True, "assign_none"))

    return checks


def run_isinstance_chain_narrowing() -> bool:
    checks: list[bool] = []

    # 4-member union: int | str | list[int] | None
    checks.extend(check_chain(10))
    checks.extend(check_chain("hello"))
    checks.extend(check_chain([1, 2, 3]))
    checks.extend(check_chain(None))

    # 2-member union: str | int, else branch narrows to int
    checks.extend(check_two_member("abc"))
    checks.extend(check_two_member(7))

    # assign narrowed value to typed variable
    checks.extend(check_assign_after_narrow(42))
    checks.extend(check_assign_after_narrow("foo"))
    checks.extend(check_assign_after_narrow(None))

    return py_assert_all(checks, "isinstance_chain_narrowing")


if __name__ == "__main__":
    print(run_isinstance_chain_narrowing())
