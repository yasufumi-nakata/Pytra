from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_str_find_index() -> bool:
    s: str = "hello world hello"
    checks: list[bool] = []

    # find / rfind
    checks.append(py_assert_eq(s.find("world"), 6, "find world"))
    checks.append(py_assert_eq(s.find("xyz"), -1, "find missing"))
    checks.append(py_assert_eq(s.rfind("hello"), 12, "rfind hello"))
    checks.append(py_assert_eq(s.rfind("xyz"), -1, "rfind missing"))

    # index (raises ValueError if not found, so only test found case)
    checks.append(py_assert_eq(s.index("world"), 6, "index world"))
    checks.append(py_assert_eq(s.index("hello"), 0, "index hello first"))

    # index raises ValueError — catch it
    caught: bool = False
    try:
        _pos: int = s.index("xyz")
    except ValueError:
        caught = True
    checks.append(py_assert_eq(caught, True, "index missing raises ValueError"))

    return py_assert_all(checks, "str_find_index")


if __name__ == "__main__":
    print(run_str_find_index())
