from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_any_dict_items() -> bool:
    root: dict[str, int | str | dict[str, int]] = {
        "meta": {"a": 2, "b": 3},
        "name": "demo",
    }

    total: int = 0
    meta_val: int | str | dict[str, int] = root.get("meta", {})
    if isinstance(meta_val, dict):
        for _k, v in meta_val.items():
            total += v

    name_val: int | str | dict[str, int] = root.get("name", "")
    checks: list[bool] = []
    checks.append(py_assert_eq(total, 5, "sum meta"))
    checks.append(py_assert_eq(str(name_val), "demo", "name"))
    return py_assert_all(checks, "any_dict_items")


if __name__ == "__main__":
    print(run_any_dict_items())
