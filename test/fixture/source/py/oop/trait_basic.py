from pytra.utils.assertions import py_assert_stdout


class _IdentityDecorator:
    def __call__(self, cls: object) -> object:
        return cls


class _ImplementsFactory:
    def __call__(self, *_traits: object) -> object:
        return _IdentityDecorator()


trait = _IdentityDecorator()
implements = _ImplementsFactory()


@trait
class Drawable:
    def draw(self) -> str: ...


@trait
class ShapeLike(Drawable):
    def area(self) -> int: ...


@trait
class Named:
    def name(self) -> str: ...


@implements(ShapeLike, Named)
class Circle:
    def draw(self) -> str:
        return "circle"

    def area(self) -> int:
        return 42

    def name(self) -> str:
        return "unit"


def render(d: Drawable) -> str:
    return d.draw()


def label(n: Named) -> str:
    return n.name()


def _case_main() -> None:
    c = Circle()
    print(render(c))
    print(label(c))
    print(c.area())
    print(isinstance(c, Drawable))
    print(isinstance(c, ShapeLike))
    print(isinstance(c, Named))


if __name__ == "__main__":
    print(py_assert_stdout(["circle", "unit", "42", "True", "True", "True"], _case_main))
