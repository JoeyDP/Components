import pytest
from typing import Tuple

from components import Component


def test_create():
    class Comp(Component):
        def __init__(self, a, b=3):
            self.a = a
            self.b = b

    c = Comp(4, b=5)
    assert c.get_params() == {'a': 4, 'b': 5}
    assert c.a == 4 and c.b == 5


def test_create_parent():
    class Comp(Component):
        def __init__(self, a):
            self.a = a

    class ParentComp(Comp):
        def __init__(self, a, b=3):
            super().__init__(a)
            self.b = b

    c = Comp(8)
    assert c.get_params() == {'a': 8}
    assert c.a == 8
    c = ParentComp(4, b=5)
    assert c.get_params() == {'a': 4, 'b': 5}
    assert c.a == 4 and c.b == 5


def test_create_parent_kwargs():
    class Comp(Component):
        def __init__(self, a):
            self.a = a

    class ParentComp(Comp):
        # we need to mention all parameters explicitly, they are not inherited.
        def __init__(self, b, **kwargs):
            super().__init__(a=3)
            self.b = b
            self.c = kwargs.pop('c', 5)

    c = Comp(8)
    assert c.get_params() == {'a': 8}
    c = ParentComp(4, a=5)
    assert c.get_params() == {'a': 5, 'b': 4}
    assert c.a == 3 and c.b == 4 and c.c == 5
    c = ParentComp(4, a=5, c=42)
    assert c.get_params() == {'a': 5, 'b': 4, 'c': 42}
    assert c.a == 3 and c.b == 4 and c.c == 42
    c = Comp(7)
    assert c.get_params() == {'a': 7}


def test_attribute_default():
    class Comp(Component):
        def __init__(self, key=5):
            self.key = key

    c = Comp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5
    c = Comp(key=3)
    assert c.get_params() == {'key': 3}
    assert c.key == 3
    c = Comp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5


def test_identifier():
    class Comp(Component):
        def __init__(self, par1=3, par2="hello"):
            self.par1 = par1

    c = Comp()
    assert c.name == "Comp"
    assert c.identifier == "Comp(par1=3, par2='hello')"
    c = Comp(5)
    assert c.identifier == "Comp(par1=5, par2='hello')"


def test_identifier_subcomp():
    class SubComp(Component):
        def __init__(self, par2="hello"):
            self.par2 = par2

    class Comp(Component):
        def __init__(self, sub: SubComp, par1=3):
            self.par1 = par1
            self.sub = sub

    c = Comp.resolve()
    assert c.name == "Comp"
    assert c.identifier == "Comp(sub=SubComp(...), par1=3)"
    assert c.full_identifier == "Comp(sub=SubComp(par2='hello'), par1=3)"
    c = Comp.resolve(par1=5, par2="world")
    assert c.identifier == "Comp(sub=SubComp(...), par1=5)"
    assert c.full_identifier == "Comp(sub=SubComp(par2='world'), par1=5)"


def test_identifier_list():
    class SubComp(Component):
        def __init__(self, idx):
            self.idx = idx

    class Comp(Component):
        def __init__(self, pars: Tuple[Component, ...]):
            self.pars = pars

    c = Comp(pars=(SubComp(1), SubComp(2)))
    assert c.identifier == "Comp(pars=(SubComp(...), SubComp(...)))"
    assert c.full_identifier == "Comp(pars=(SubComp(idx=1), SubComp(idx=2)))"


def test_init_non_identifying_params():
    class SubComp(Component):
        def __init__(self, _par2="hello"):
            self.par2 = _par2

    class Comp(Component):
        par2 = "test"
        def __init__(self, _sub: SubComp, _par1=3):
            self.par1 = _par1
            self.sub = _sub

    c = Comp(SubComp())
    assert c.par1 == 3 and c.sub.par2 == "hello"
    c = Comp.resolve()
    assert c.par1 == 3 and c.sub.par2 == "test"
    c = Comp.resolve(par1=5, par2="world")
    assert c.par1 == 5 and c.sub.par2 == "world"
    c = Comp.resolve(sub_par2="123")
    assert c.sub.par2 == "123"
    c = Comp.resolve(_sub_par2="456")
    assert c.sub.par2 == "456"
    c = Comp.resolve(_par1=9, _par2="!")
    assert c.par1 == 9 and c.sub.par2 == "!"


def test_identifier_non_identifying_params():
    class SubComp(Component):
        def __init__(self, _par2="hello"):
            self.par2 = _par2

    class Comp(Component):
        def __init__(self, sub: SubComp, _par1=3):
            self.par1 = _par1
            self.sub = sub

    c = Comp.resolve()
    assert c.identifier == "Comp(sub=SubComp(...))"
    assert c.full_identifier == "Comp(sub=SubComp())"
    c = Comp.resolve(par1=5, par2="world")
    assert c.identifier == "Comp(sub=SubComp(...))"
    assert c.full_identifier == "Comp(sub=SubComp())"
    c = Comp.resolve(_par1=9, _par2="!")
    assert c.identifier == "Comp(sub=SubComp(...))"
    assert c.full_identifier == "Comp(sub=SubComp())"


def test_non_identifying_params_subcomp():
    class SubComp(Component):
        def __init__(self, idx=1):
            self.idx = idx

    class Comp(Component):
        def __init__(self, _par: SubComp):
            self.par = _par

    c = Comp.resolve()
    assert c.par.idx == 1
    c = Comp.resolve(_par=SubComp(2))
    assert c.par.idx == 2
    c = Comp.resolve(par=SubComp(3))
    assert c.par.idx == 3


def test_identifier_non_identifying_params_subcomp():
    class SubComp(Component):
        def __init__(self, idx=1):
            self.idx = idx

    class Comp(Component):
        def __init__(self, _par: SubComp):
            self.par = _par

    c = Comp.resolve()
    assert c.identifier == "Comp()"
    assert c.full_identifier == "Comp()"
    c = Comp.resolve(_par=SubComp(2))
    assert c.identifier == "Comp()"
    assert c.full_identifier == "Comp()"
    c = Comp.resolve(par=SubComp(3))
    assert c.identifier == "Comp()"
    assert c.full_identifier == "Comp()"


def test_identifier_non_identifying_params_list():
    class SubComp(Component):
        def __init__(self, idx):
            self.idx = idx

    class Comp(Component):
        def __init__(self, _pars: Tuple[Component, ...]):
            self.pars = _pars

    c = Comp.resolve(pars=(SubComp(1), SubComp(2)))
    assert c.identifier == "Comp()"
    assert c.full_identifier == "Comp()"
    c = Comp(_pars=(SubComp(1), SubComp(2)))
    assert c.identifier == "Comp()"
    assert c.full_identifier == "Comp()"
