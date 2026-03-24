# pytra: builtin-declarations
"""コンテナ型の dunder + メソッド宣言。

resolve がメソッドシグネチャを参照して型解決する。emit 対象外。
@template でクラスレベル型パラメータを宣言する。
引数の型は exact match（暗黙変換なし）。

spec: docs/ja/spec/spec-builtin-functions.md §4
"""

from pytra.std.template import template


# ---------------------------------------------------------------------------
# §4.1 list
# ---------------------------------------------------------------------------

@template("T")
class list:
    def __len__(self) -> int: pass
    def __str__(self) -> str: pass
    def __bool__(self) -> bool: pass
    def __iter__(self) -> Iterator[T]: pass
    def append(self, x: T) -> None: pass
    def extend(self, x: list[T]) -> None: pass
    def pop(self, index: int = -1) -> T: pass
    def insert(self, index: int, x: T) -> None: pass
    def remove(self, x: T) -> None: pass
    def clear(self) -> None: pass
    def reverse(self) -> None: pass
    def sort(self) -> None: pass
    def copy(self) -> list[T]: pass
    def index(self, x: T) -> int: pass
    def count(self, x: T) -> int: pass


# ---------------------------------------------------------------------------
# §4.2 str
# ---------------------------------------------------------------------------

class str:
    def __len__(self) -> int: pass
    def __str__(self) -> str: pass
    def __bool__(self) -> bool: pass
    def __int__(self) -> int: pass
    def __float__(self) -> float: pass
    def upper(self) -> str: pass
    def lower(self) -> str: pass
    def strip(self) -> str: pass
    def lstrip(self) -> str: pass
    def rstrip(self) -> str: pass
    def split(self, sep: str = " ") -> list[str]: pass
    def join(self, parts: list[str]) -> str: pass
    def startswith(self, prefix: str) -> bool: pass
    def endswith(self, suffix: str) -> bool: pass
    def find(self, sub: str) -> int: pass
    def rfind(self, sub: str) -> int: pass
    def replace(self, old: str, new: str) -> str: pass
    def isdigit(self) -> bool: pass
    def isalpha(self) -> bool: pass
    def isalnum(self) -> bool: pass
    def isupper(self) -> bool: pass
    def islower(self) -> bool: pass
    def zfill(self, width: int) -> str: pass
    def count(self, sub: str) -> int: pass


# ---------------------------------------------------------------------------
# §4.3 dict
# ---------------------------------------------------------------------------

@template("K", "V")
class dict:
    def __len__(self) -> int: pass
    def __str__(self) -> str: pass
    def __bool__(self) -> bool: pass
    def keys(self) -> list[K]: pass
    def values(self) -> list[V]: pass
    def items(self) -> list[tuple[K, V]]: pass
    def get(self, key: K, default: V = None) -> V: pass
    def pop(self, key: K) -> V: pass
    def setdefault(self, key: K, default: V = None) -> V: pass
    def clear(self) -> None: pass
    def update(self, other: dict[K, V]) -> None: pass


# ---------------------------------------------------------------------------
# §4.4 set
# ---------------------------------------------------------------------------

@template("T")
class set:
    def __len__(self) -> int: pass
    def __str__(self) -> str: pass
    def __bool__(self) -> bool: pass
    def add(self, x: T) -> None: pass
    def discard(self, x: T) -> None: pass
    def remove(self, x: T) -> None: pass
    def clear(self) -> None: pass


# ---------------------------------------------------------------------------
# §4.5 tuple
# ---------------------------------------------------------------------------

class tuple:
    def __len__(self) -> int: pass
    def __str__(self) -> str: pass
    def __bool__(self) -> bool: pass
