from pytra.utils.assertions import py_assert_all, py_assert_eq


def test_object_dict_items_unpack() -> list[bool]:
    """dict[str, object].items() の tuple unpack"""
    checks: list[bool] = []
    d: dict[str, object] = {"name": "alice", "age": 30}
    keys: list[str] = []
    for key, value in d.items():
        keys.append(key)
    checks.append(py_assert_eq(len(keys), 2, "obj_items_count"))
    return checks


def test_object_list_index() -> list[bool]:
    """list[object][i] の typed access"""
    checks: list[bool] = []
    elems: list[object] = [10, 20, 30]
    first: object = elems[0]
    last: object = elems[2]
    checks.append(py_assert_eq(str(first), "10", "obj_list_first"))
    checks.append(py_assert_eq(str(last), "30", "obj_list_last"))

    i: int = 1
    mid: object = elems[i]
    checks.append(py_assert_eq(str(mid), "20", "obj_list_var_index"))
    return checks


def test_object_dict_get() -> list[bool]:
    """dict[str, object].get() の戻り値"""
    checks: list[bool] = []
    node: dict[str, object] = {"resolved_type": "int64", "name": "x"}
    rt: str = str(node.get("resolved_type", ""))
    checks.append(py_assert_eq(rt, "int64", "obj_dict_get_existing"))

    missing: str = str(node.get("missing_key", "default"))
    checks.append(py_assert_eq(missing, "default", "obj_dict_get_default"))
    return checks


def test_str_no_unnecessary_unbox() -> list[bool]:
    """既に str な値に不要な unbox をしない"""
    checks: list[bool] = []

    # plain str passthrough
    s: str = "hello"
    result: str = s
    checks.append(py_assert_eq(result, "hello", "str_passthrough"))

    # str field access — should not unbox
    d: dict[str, str] = {"key": "value"}
    v: str = d.get("key", "")
    checks.append(py_assert_eq(v, "value", "str_dict_get_no_unbox"))

    # str from object dict — needs str() cast but not unbox
    od: dict[str, object] = {"name": "world"}
    name: str = str(od.get("name", ""))
    checks.append(py_assert_eq(name, "world", "str_from_object_dict"))
    return checks


def test_set_tuple_keys() -> list[bool]:
    """set[tuple[str, str]] — tuple をキーとする set"""
    checks: list[bool] = []
    seen: set[tuple[str, str]] = set()
    seen.add(("base", "trait"))
    seen.add(("foo", "bar"))
    seen.add(("base", "trait"))  # duplicate

    checks.append(py_assert_eq(len(seen), 2, "set_tuple_size"))
    checks.append(py_assert_eq(("base", "trait") in seen, True, "set_tuple_contains"))
    checks.append(py_assert_eq(("x", "y") in seen, False, "set_tuple_not_contains"))
    return checks


def run_object_container_access() -> bool:
    checks: list[bool] = []
    checks.extend(test_object_dict_items_unpack())
    checks.extend(test_object_list_index())
    checks.extend(test_object_dict_get())
    checks.extend(test_str_no_unnecessary_unbox())
    checks.extend(test_set_tuple_keys())
    return py_assert_all(checks, "object_container_access")


if __name__ == "__main__":
    print(run_object_container_access())
