import pytest

from components import Component


def test_create():
    class Comp(Component):
        def __init__(self, a, b=3):
            pass

    # c = Comp(3, b=5)
    # assert c.get_params() == {'a': 3, 'b': 5}


def test_create_parent():
    class Comp(Component):
        def __init__(self, a):
            pass

    class ParentComp(Comp):
        def __init__(self, a, b=3):
            super().__init__(a)

    # c1 = Comp(8)
    # assert c1.get_params() == {'a': 8}
    # c2 = ParentComp(4, b=5)
    # assert c2.get_params() == {'a': 4, 'b': 5}


def test_create_parent_kwargs():
    class Comp(Component):
        def __init__(self, a):
            print("a", a)

    class ParentComp(Comp):
        # by using **kwargs, we indicate that parent parameters should be included as well.
        def __init__(self, b, **kwargs):
            super().__init__(**kwargs)

    # c1 = Comp(8)
    # assert c1.get_params() == {'a': 8}
    # c2 = ParentComp(4, a=5)
    # assert c2.get_params() == {'a': 5, 'b': 4}


def test_attribute_default():
    class Comp(Component):
        def __init__(self, key=5):
            pass

    # c1 = Comp()
    # assert c1.get_params() == {'key': 5}
    # c2 = Comp(key=3)
    # assert c2.get_params() == {'key': 3}
    # c3 = Comp()
    # assert c3.get_params() == {'key': 5}


def test_attribute_override_default():
    class Comp(Component):
        key = 3
        def __init__(self, key=5):
            pass

    # c1 = Comp()
    # assert c1.get_params() == {'key': 3}
    # c2 = Comp(key=7)
    # assert c2.get_params() == {'key': 7}
    # c3 = Comp()
    # assert c3.get_params() == {'key': 3}


def test_attribute_override_from_owner():
    class SubComp(Component):
        def __init__(self, key=5):
            pass

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    # TODO: test


def test_attribute_override_with_owner():
    class SubComp(Component):
        key = 3
        def __init__(self, key=5):
            pass

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    # TODO: test


def test_attribute_override_conflict_owner():
    class SubComp(Component):
        key = 3
        def __init__(self, key=5):
            pass

    class Comp(Component):
        key = 7
        def __init__(self, sub: SubComp):
            self.sub = sub

    # TODO: test


def test_component_override():
    class SubComp(Component):
        def __init__(self):
            pass

    class OtherComp(SubComp):
        pass

    class Comp(Component):
        sub: OtherComp
        def __init__(self, sub: SubComp):
            self.sub = sub

    # TODO: test


def test_component_override_parent():
    class SubComp(Component):
        pass

    class OtherComp(SubComp):
        pass

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    class ParentComp(Comp):
        sub: OtherComp

    print()
    print(ParentComp.__init__.__annotations__)
    print(ParentComp.__annotations__)

    # TODO: test

