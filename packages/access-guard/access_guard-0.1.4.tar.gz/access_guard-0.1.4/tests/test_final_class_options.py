import pytest
from access_guard import Access, final_class


def test_final_class_exclude_allows_override():
    @final_class(exclude={"open"})
    class Base(metaclass=Access):
        def open(self):
            return 1
        def close(self):
            return 2

    # close 應為 final, open 不應 final
    class Child(Base):
        def open(self):  # allowed override
            return 10

    c = Child()
    assert c.open() == 10
    assert c.close() == 2

    with pytest.raises(RuntimeError):
        class Bad(Base):  # noqa: F811
            def close(self):  # not allowed override
                return 9


def test_final_class_include_magic():
    @final_class(include_magic=True)
    class Base(metaclass=Access):
        def __repr__(self):  # should become final
            return "Base()"
        def run(self):
            return 1

    with pytest.raises(RuntimeError):
        class Bad(Base):  # noqa: F811
            def __repr__(self):  # type: ignore
                return "Bad()"

    with pytest.raises(RuntimeError):
        Base.__repr__ = lambda self: "hack"  # type: ignore
