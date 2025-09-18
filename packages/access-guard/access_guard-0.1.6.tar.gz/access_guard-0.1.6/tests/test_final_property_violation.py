import pytest
from access_guard import Access, final


def test_property_override_violation():
    class Base(metaclass=Access):
        @property
        @final
        def value(self):
            return 10

    with pytest.raises(RuntimeError):
        class Bad(Base):  # noqa: F811
            @property
            def value(self):  # type: ignore
                return 11


def test_property_dynamic_assignment_violation():
    class Base(metaclass=Access):
        @property
        @final
        def value(self):
            return 10

    class Child(Base):
        pass

    def new_prop(self):  # pragma: no cover
        return 99

    with pytest.raises(RuntimeError):
        Child.value = property(new_prop)  # type: ignore
