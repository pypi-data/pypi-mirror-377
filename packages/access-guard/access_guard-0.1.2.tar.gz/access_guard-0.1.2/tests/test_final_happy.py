from access_guard import Access, final


def test_happy_path():
    class Base(metaclass=Access):
        @final
        def stable(self):
            return 1

        @property
        @final
        def value(self):  # property final
            return 10

    class Child(Base):
        def other(self):
            return self.stable() + self.value

    c = Child()
    assert c.stable() == 1
    assert c.value == 10
    assert c.other() == 11
