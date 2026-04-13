"""for loop over function return value without local type annotation.

Verifies that EAST infers the loop variable type from the callee's
return type annotation when the local variable has no explicit annotation.
"""


from pytra.utils.assertions import py_assert_stdout


def get_words() -> list[str]:
    return ["hello", "world", "foo"]


def get_nums() -> list[int]:
    return [10, 20, 30]


def join_words() -> str:
    words = get_words()
    result: str = ""
    for w in words:
        if result != "":
            result = result + ","
        result = result + w
    return result


def sum_nums() -> int:
    nums = get_nums()
    total: int = 0
    for n in nums:
        total = total + n
    return total


def _case_main() -> None:
    print(join_words())
    print(sum_nums())


if __name__ == "__main__":
    print(py_assert_stdout(["hello,world,foo", "60"], _case_main))
