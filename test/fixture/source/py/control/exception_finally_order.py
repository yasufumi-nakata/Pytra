def leaf() -> None:
    raise ValueError("boom")


if __name__ == "__main__":
    try:
        try:
            leaf()
        finally:
            print("cleanup")
    except ValueError:
        print("caught")
