from pytra.utils.assertions import py_assert_all, py_assert_eq, py_assert_true


def run_union_basic() -> bool:
    payload: dict[str, int | str | dict[str, int]] = {
        "n": 1,
        "s": "x",
        "m": {"k": 2},
    }
    values: list[int | str] = []
    values.append(payload["n"])
    values.append(payload["s"])
    n_value: int = int(values[0])
    s_value: str = str(values[1])

    nested_val: int | str | dict[str, int] = payload.get("m", {})
    total: int = 0
    if isinstance(nested_val, dict):
        for _k, v in nested_val.items():
            total += v

    checks: list[bool] = []
    checks.append(py_assert_eq(n_value, 1, "union list int"))
    checks.append(py_assert_eq(s_value, "x", "union list str"))
    checks.append(py_assert_eq(total, 2, "dict[str,union].get(...).items()"))
    checks.append(py_assert_true(isinstance(payload["m"], dict), "union dict type"))
    return py_assert_all(checks, "union_basic")


if __name__ == "__main__":
    print(run_union_basic())
