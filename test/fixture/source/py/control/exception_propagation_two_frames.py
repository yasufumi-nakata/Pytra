def leaf() -> None:
    raise ValueError("boom")


def middle() -> None:
    leaf()


def outer() -> None:
    middle()


if __name__ == "__main__":
    try:
        outer()
    except ValueError as err:
        print("caught", err)
