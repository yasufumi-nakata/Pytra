# self_hosted parser signature test: class inline method `def ...: return ...` is accepted.
from __future__ import annotations


class Value:
    def __pow__(self, other: Value) -> Value:
        return self


if __name__ == "__main__":
    v: Value = Value()
    print(type(v).__name__)
