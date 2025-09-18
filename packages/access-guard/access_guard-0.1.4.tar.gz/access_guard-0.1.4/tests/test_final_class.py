import pytest
from access_guard import Access, final_class


def test_final_class_prevents_override():
    @final_class
    class Base(metaclass=Access):
        def a(self):
            return 1
        def b(self):
            return 2

    class Child(Base):
        pass

    c = Child()
    assert c.a() == 1
    assert c.b() == 2

    with pytest.raises(RuntimeError):
        class Bad(Base):  # noqa: F811
            def a(self):  # type: ignore
                return 9


def test_final_class_dynamic_assignment_blocked():
    @final_class
    class Base(metaclass=Access):
        def run(self):
            return 5

    class Child(Base):
        pass

    def hacked(self):  # pragma: no cover
        return 999

    with pytest.raises(RuntimeError):
        Child.run = hacked  # type: ignore
