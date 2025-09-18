import pytest
from access_guard import Access, final


def test_override_violation_at_class_creation():
    class Base(metaclass=Access):
        @final
        def stable(self):
            return 1

    with pytest.raises(RuntimeError):
        class Bad(Base):  # noqa: F811
            def stable(self):  # attempt to override final
                return 2


def test_dynamic_assignment_violation():
    class Base(metaclass=Access):
        @final
        def stable(self):
            return 1

    class Child(Base):
        pass

    def hacked(self):
        return 999

    with pytest.raises(RuntimeError):
        Child.stable = hacked  # type: ignore
