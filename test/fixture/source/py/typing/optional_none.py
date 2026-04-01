from pytra.utils.assertions import py_assert_all, py_assert_eq, py_assert_true


def run_optional_none() -> bool:
    v: str | None = None
    w: str | None = "x"

    is_none_v: bool = v is None
    is_not_none_w: bool = w is not None

    out: str = "fallback" if v is None else str(v)

    checks: list[bool] = []
    checks.append(py_assert_true(is_none_v, "v is None"))
    checks.append(py_assert_true(is_not_none_w, "w is not None"))
    checks.append(py_assert_eq(out, "fallback", "none fallback"))
    return py_assert_all(checks, "optional_none")


if __name__ == "__main__":
    print(run_optional_none())
