from pytra.utils.assertions import py_assert_all, py_assert_eq


def test_str_list_int() -> list[bool]:
    checks: list[bool] = []
    xs: list[int] = [1, 2, 3]
    checks.append(py_assert_eq(str(xs), "[1, 2, 3]", "str_list_int"))
    checks.append(py_assert_eq(str([]), "[]", "str_list_empty"))
    checks.append(py_assert_eq(str([42]), "[42]", "str_list_single"))
    return checks


def test_str_list_str() -> list[bool]:
    checks: list[bool] = []
    xs: list[str] = ["a", "b", "c"]
    checks.append(py_assert_eq(str(xs), "['a', 'b', 'c']", "str_list_str"))
    return checks


def test_str_list_bool() -> list[bool]:
    checks: list[bool] = []
    xs: list[bool] = [True, False, True]
    checks.append(py_assert_eq(str(xs), "[True, False, True]", "str_list_bool"))
    return checks


def test_str_dict() -> list[bool]:
    checks: list[bool] = []
    d: dict[str, int] = {"a": 1, "b": 2}
    s: str = str(d)
    # dict の str 表現はキー順序が挿入順
    checks.append(py_assert_eq(s, "{'a': 1, 'b': 2}", "str_dict"))
    checks.append(py_assert_eq(str({}), "{}", "str_dict_empty"))
    return checks


def test_str_tuple() -> list[bool]:
    checks: list[bool] = []
    t: tuple[int, str] = (1, "x")
    checks.append(py_assert_eq(str(t), "(1, 'x')", "str_tuple"))
    checks.append(py_assert_eq(str((42,)), "(42,)", "str_tuple_single"))
    return checks


def test_str_nested() -> list[bool]:
    checks: list[bool] = []
    nested: list[list[int]] = [[1, 2], [3, 4]]
    checks.append(py_assert_eq(str(nested), "[[1, 2], [3, 4]]", "str_nested_list"))
    return checks


def run_str_repr_containers() -> bool:
    checks: list[bool] = []
    checks.extend(test_str_list_int())
    checks.extend(test_str_list_str())
    checks.extend(test_str_list_bool())
    checks.extend(test_str_dict())
    checks.extend(test_str_tuple())
    checks.extend(test_str_nested())
    return py_assert_all(checks, "str_repr_containers")


if __name__ == "__main__":
    print(run_str_repr_containers())
