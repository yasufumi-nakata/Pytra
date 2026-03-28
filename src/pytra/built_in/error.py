"""Pytra built-in exception classes.

These classes are transpiled through the standard pipeline to all target
languages.  No hand-written runtime exception types are needed.

Exception hierarchy:

    PytraError
    ├── ValueError
    ├── RuntimeError
    ├── FileNotFoundError
    ├── PermissionError
    ├── TypeError
    ├── IndexError
    ├── KeyError
    └── OverflowError

Users can define custom exceptions by inheriting from any of the above.
"""


class PytraError:
    msg: str

    def __init__(self, msg: str) -> None:
        self.msg = msg


class ValueError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class RuntimeError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class FileNotFoundError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class PermissionError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class TypeError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class IndexError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class KeyError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class OverflowError(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
