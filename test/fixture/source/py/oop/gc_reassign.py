# Verify that reassignment `a = b` works correctly and __del__ is syntactically valid.
#
# __del__ body is `pass` to avoid GC-timing-dependent stdout.
# All languages (RC and GC) can pass this test.


class Tracked:
    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        pass


def run_gc_reassign() -> None:
    a = Tracked("A")
    b = Tracked("B")
    print("before reassign")
    a = b
    print("after reassign")
    print(a.name)


def _case_main() -> None:
    run_gc_reassign()

if __name__ == "__main__":
    _case_main()
