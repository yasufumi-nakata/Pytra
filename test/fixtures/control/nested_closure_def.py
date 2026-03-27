def outer(seed: int, bump: int) -> int:
    x: int = seed
    scale: int = 2

    def inner(y: int) -> int:
        return x + scale + y

    def rec(n: int) -> int:
        if n <= 0:
            return 0
        return rec(n - 1) + bump

    x = x + bump
    return inner(3) + rec(2)


print(outer(10, 5))
