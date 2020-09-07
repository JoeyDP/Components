import pytest

from components import Component


def test_resolve_component():
    class Comp(Component):
        def __init__(self, a, b=3):
            self.a = a
            self.b = b

    c = Comp.resolve(a=4)
    assert c.get_params() == {'a': 4, 'b': 3}
    assert c.a == 4 and c.b == 3
    c = Comp.resolve(a=4, b=5)
    assert c.get_params() == {'a': 4, 'b': 5}
    assert c.a == 4 and c.b == 5

    with pytest.raises(TypeError):
        with pytest.warns(RuntimeWarning):
            Comp.resolve()
    with pytest.raises(TypeError):
        with pytest.warns(RuntimeWarning):
            Comp.resolve(b=5)
    with pytest.raises(TypeError):
        with pytest.warns(RuntimeWarning):
            Comp.resolve(other_param=3)


def test_attribute_override_default():
    class Comp(Component):
        key = 3

        def __init__(self, key=5):
            self.key = key

    # Use `resolve` to check attributes
    c = Comp.resolve()
    assert c.get_params() == {'key': 3}
    assert c.key == 3
    c = Comp.resolve(key=9)
    assert c.get_params() == {'key': 9}
    assert c.key == 9
    # Normal object creation ignores attribute override for parameter 'key'
    c = Comp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5
    c = Comp(key=7)
    assert c.get_params() == {'key': 7}
    assert c.key == 7


def test_resolve_subcomponent():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve(key=4)
    assert c.get_params()['sub'].get_params() == {'key': 4}
    assert c.sub.key == 4
    c = Comp.resolve(sub_key=42)
    assert c.get_params()['sub'].get_params() == {'key': 42}
    assert c.sub.key == 42
    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'key': 5}
    assert c.sub.key == 5
    c = Comp.resolve(sub=SubComp(8))
    assert c.get_params()['sub'].get_params() == {'key': 8}
    assert c.sub.key == 8

    with pytest.warns(RuntimeWarning):
        c = Comp.resolve(sub=3)
        assert c.sub == 3
    with pytest.raises(TypeError):
        Comp.resolve(par1=42)
    with pytest.raises(TypeError):
        Comp.resolve(sub=SubComp(8), key=5)


def test_resolve_subcomponent_conflicting_params():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp, key=3):
            self.sub = sub
            self.key = key

    with pytest.raises(TypeError):
        Comp.resolve(other_key=42)

    c = Comp.resolve()
    assert c.get_params()['key'] == 3 and c.get_params()['sub'].get_params() == {'key': 5}
    assert c.key == 3 and c.sub.key == 5
    c = Comp.resolve(key=42)
    assert c.get_params()['key'] == 42 and c.get_params()['sub'].get_params() == {'key': 5}
    assert c.key == 42 and c.sub.key == 5
    c = Comp.resolve(sub_key=8)
    assert c.get_params()['key'] == 3 and c.get_params()['sub'].get_params() == {'key': 8}
    assert c.key == 3 and c.sub.key == 8
    c = Comp.resolve(key=10, sub_key=1)
    assert c.get_params()['key'] == 10 and c.get_params()['sub'].get_params() == {'key': 1}
    assert c.key == 10 and c.sub.key == 1


def test_subcomponent_shadowed_param():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp, key=3):
            self.sub = sub
            self.key = key

    class OtherComp(Component):
        sub: Comp

        def __init__(self, sub: Comp):
            self.sub = sub

    c = OtherComp.resolve()
    assert type(c.sub) == Comp
    assert type(c.sub.sub) == SubComp

    with pytest.warns(RuntimeWarning):
        c = OtherComp.resolve(sub=None)
        assert (c.sub is None)


def test_resolve_conflicting_subcomponent_params():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub1: SubComp, sub2: SubComp):
            self.sub1 = sub1
            self.sub2 = sub2

    with pytest.raises(TypeError):
        Comp.resolve(key=42)

    with pytest.raises(TypeError):
        Comp.resolve(other_key=42)

    c = Comp.resolve()
    assert c.get_params()['sub1'].get_params() == {'key': 5} and c.get_params()['sub2'].get_params() == {'key': 5}
    assert c.sub1.key == 5 and c.sub2.key == 5
    c = Comp.resolve(sub1_key=3)
    assert c.get_params()['sub1'].get_params() == {'key': 3} and c.get_params()['sub2'].get_params() == {'key': 5}
    assert c.sub1.key == 3 and c.sub2.key == 5
    c = Comp.resolve(sub2_key=8)
    assert c.get_params()['sub1'].get_params() == {'key': 5} and c.get_params()['sub2'].get_params() == {'key': 8}
    assert c.sub1.key == 5 and c.sub2.key == 8
    c = Comp.resolve(sub1_key=9, sub2_key=42)
    assert c.get_params()['sub1'].get_params() == {'key': 9} and c.get_params()['sub2'].get_params() == {'key': 42}
    assert c.sub1.key == 9 and c.sub2.key == 42


def test_subcomponent_type_mismatch_warn():
    class SubComp(Component):
        def __init__(self, key: str = 5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    with pytest.warns(RuntimeWarning):
        Comp.resolve()
    with pytest.warns(RuntimeWarning):
        Comp.resolve(key=20)
    with pytest.warns(None):
        Comp.resolve(key="20")


def test_subcomponent_change_type_mismatch_warn():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        key: str

        def __init__(self, sub: SubComp):
            self.sub = sub

    with pytest.warns(RuntimeWarning):
        Comp.resolve()
    with pytest.warns(RuntimeWarning):
        Comp.resolve(key=20)


def test_subcomponent_change_type_mismatch_warn2():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        sub_key: str

        def __init__(self, sub: SubComp):
            self.sub = sub

    with pytest.warns(RuntimeWarning):
        Comp.resolve()
    with pytest.warns(RuntimeWarning):
        Comp.resolve(key=20)


def test_subcomponent_conflicting_param_type_are_conflicts_removed():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        # type should not be changed because of conflicting names
        key: str

        def __init__(self, sub1: SubComp, sub2: SubComp):
            self.sub1 = sub1
            self.sub2 = sub2

    # Capture warning
    with pytest.warns(None) as record:
        Comp.resolve()
        Comp.resolve(sub1_key=20)
        Comp.resolve(sub2_key=30)

    for warning in record:
        assert False, f"Warning should not have been given: {warning}"
    assert len(record) == 0, "No warning should be given."


def test_subcomponent_conflicting_param_type_shadow_handled_1():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        # type of subcomp key should not be changed because of conflicting names and parent
        key: str

        def __init__(self, sub1: SubComp, sub2: SubComp, key: int):
            self.key = key
            self.sub1 = sub1
            self.sub2 = sub2

    with pytest.warns(RuntimeWarning):
        Comp.resolve(key=123)
    with pytest.warns(RuntimeWarning):
        Comp.resolve(key="123", sub1_key="456")
    with pytest.warns(RuntimeWarning):
        Comp.resolve(key="123", sub1_key="13")

    # Capture warning
    with pytest.warns(None) as record:
        Comp.resolve(key="123")
        Comp.resolve(key="123", sub1_key=20)
        Comp.resolve(key="123", sub2_key=30)

    for warning in record:
        assert False, f"Warning should not have been given: {warning}"
    assert len(record) == 0, "No warning should be given."


def test_subcomponent_conflicting_param_type_shadow_handled_2():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        # type of subcomp key should not be changed because of conflicting names and parent
        key: str

        def __init__(self, sub: SubComp, key: int):
            self.key = key
            self.sub1 = sub

    with pytest.warns(RuntimeWarning):
        Comp.resolve(key=123)
    with pytest.warns(RuntimeWarning):
        Comp.resolve(key="123", sub_key="456")

    # Capture warning
    with pytest.warns(None) as record:
        Comp.resolve(key="123")
        Comp.resolve(key="123", sub_key=20)

    for warning in record:
        assert False, f"Warning should not have been given: {warning}"
    assert len(record) == 0, "No warning should be given."


def test_resolve_conflicting_params():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp, key=4):
            self.sub = sub
            self.key = key

    with pytest.raises(TypeError):
        Comp.resolve(other_key=42)

    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'key': 5} and c.get_params()['key'] == 4
    assert c.sub.key == 5 and c.key == 4
    c = Comp.resolve(sub_key=3)
    assert c.get_params()['sub'].get_params() == {'key': 3} and c.get_params()['key'] == 4
    assert c.sub.key == 3 and c.key == 4
    c = Comp.resolve(key=8)
    assert c.get_params()['sub'].get_params() == {'key': 5} and c.get_params()['key'] == 8
    assert c.sub.key == 5 and c.key == 8
    c = Comp.resolve(sub_key=9, key=42)
    assert c.get_params()['sub'].get_params() == {'key': 9} and c.get_params()['key'] == 42
    assert c.sub.key == 9 and c.key == 42


def test_resolve_conflicting_subcomponent_params_2():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub1: SubComp, sub2: SubComp, key=42):
            self.sub1 = sub1
            self.sub2 = sub2
            self.key = key

    with pytest.raises(TypeError):
        Comp.resolve(other_key=42)

    c = Comp.resolve()
    assert c.get_params()['sub1'].get_params() == {'key': 5} and c.get_params()['sub2'].get_params() == {'key': 5} and \
           c.get_params()['key'] == 42
    assert c.sub1.key == 5 and c.sub2.key == 5 and c.key == 42
    c = Comp.resolve(sub1_key=9, sub2_key=12, key=3)
    assert c.get_params()['sub1'].get_params() == {'key': 9} and c.get_params()['sub2'].get_params() == {'key': 12} and \
           c.get_params()['key'] == 3
    assert c.sub1.key == 9 and c.sub2.key == 12 and c.key == 3


def test_attribute_override_from_owner():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        key = 3

        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve(key=4)
    assert c.get_params()['sub'].get_params() == {'key': 4}
    assert c.sub.key == 4
    assert type(c.sub) == SubComp
    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'key': 3}
    assert c.sub.key == 3
    c = SubComp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5


def test_attribute_override_conflict():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        key = 3
        sub_key = 9

        def __init__(self, sub: SubComp):
            self.sub = sub

    with pytest.raises(TypeError):
        Comp.resolve(key=4)
    c = SubComp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5
    with pytest.raises(TypeError):
        Comp.resolve()


def test_param_provide_conflict():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve(key=4)
    assert c.get_params()['sub'].get_params() == {'key': 4}
    assert c.sub.key == 4
    assert type(c.sub) == SubComp
    c = SubComp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5
    with pytest.raises(TypeError):
        Comp.resolve(key=3, sub_key=8)


def test_attribute_override_from_owner_full_name():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        sub_key = 3

        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve(key=4)
    assert c.get_params()['sub'].get_params() == {'key': 4}
    assert c.sub.key == 4
    assert type(c.sub) == SubComp
    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'key': 3}
    assert c.sub.key == 3
    c = SubComp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5


def test_attribute_override_with_owner():
    class SubComp(Component):
        key = 3

        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve(key=4)
    assert c.get_params()['sub'].get_params() == {'key': 4}
    assert c.sub.key == 4
    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'key': 3}
    assert c.sub.key == 3

    c = SubComp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5
    c = SubComp.resolve()
    assert c.get_params() == {'key': 3}
    assert c.key == 3


def test_attribute_override_both():
    class SubComp(Component):
        key = 3

        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        key = 7

        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve(key=4)
    assert c.get_params()['sub'].get_params() == {'key': 4}
    assert c.sub.key == 4
    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'key': 7}
    assert c.sub.key == 7

    c = SubComp()
    assert c.get_params() == {'key': 5}
    assert c.key == 5
    c = SubComp.resolve()
    assert c.get_params() == {'key': 3}
    assert c.key == 3


def test_component_override():
    class SubComp(Component):
        def __init__(self, par1=3):
            self.par1 = par1

    class OtherComp(Component):
        def __init__(self, par2=5):
            self.par2 = par2

    class Comp(Component):
        sub: OtherComp

        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'par2': 5}
    assert type(c.sub) == OtherComp
    c = Comp.resolve(par2=8)
    assert c.get_params()['sub'].get_params() == {'par2': 8}
    assert type(c.sub) == OtherComp
    with pytest.raises(TypeError):
        Comp.resolve(par1=42)


def test_component_override_parent():
    class SubComp(Component):
        def __init__(self, par1=3):
            self.par1 = par1

    class OtherComp(Component):
        def __init__(self, par2=5):
            self.par2 = par2

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    class ParentComp(Comp):
        sub: OtherComp

    c = ParentComp.resolve()
    assert c.get_params()['sub'].get_params() == {'par2': 5}
    assert type(c.sub) == OtherComp
    c = ParentComp.resolve(par2=8)
    assert c.get_params()['sub'].get_params() == {'par2': 8}
    assert type(c.sub) == OtherComp
    with pytest.raises(TypeError):
        ParentComp.resolve(par1=42)

    c = Comp.resolve()
    assert c.get_params()['sub'].get_params() == {'par1': 3}
    assert type(c.sub) == SubComp
    c = Comp.resolve(par1=8)
    assert c.get_params()['sub'].get_params() == {'par1': 8}
    assert type(c.sub) == SubComp
    with pytest.raises(TypeError):
        Comp.resolve(par2=42)


def test_component_override_subcomponent_type():
    class OtherComp(Component):
        def __init__(self, par2=5):
            self.par2 = par2

    class OtherComp2(Component):
        def __init__(self, par3=42):
            self.par3 = par3

    class SubComp(Component):
        def __init__(self, sub1: OtherComp, par1=3):
            self.sub1 = sub1
            self.par1 = par1

    class Comp(Component):
        sub1: OtherComp2

        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve()
    assert type(c.sub.sub1) == OtherComp2
    c = Comp.resolve(par1=2)
    assert c.sub.par1 == 2
    with pytest.raises(TypeError):
        Comp.resolve(par2=42)
    c = Comp.resolve(par3=7)
    assert c.sub.sub1.par3 == 7


def test_component_override_subcomponent_type_full_name():
    class OtherComp(Component):
        def __init__(self, par2=5):
            self.par2 = par2

    class OtherComp2(Component):
        def __init__(self, par3=42):
            self.par3 = par3

    class SubComp(Component):
        def __init__(self, sub1: OtherComp, par1=3):
            self.sub1 = sub1
            self.par1 = par1

    class Comp(Component):
        sub_sub1: OtherComp2

        def __init__(self, sub: SubComp):
            self.sub = sub

    c = Comp.resolve()
    assert type(c.sub.sub1) == OtherComp2
    c = Comp.resolve(par1=2)
    assert c.sub.par1 == 2
    with pytest.raises(TypeError):
        Comp.resolve(par2=42)
    c = Comp.resolve(par3=7)
    assert c.sub.sub1.par3 == 7


def test_parent_component_override_child_type():
    class SubComp(Component):
        pass

    class OtherComp(Component):
        pass

    class ParentComp(Component):
        sub: OtherComp

        def __init__(self):
            pass

    class Comp(ParentComp):
        def __init__(self, sub: SubComp):
            super().__init__()
            self.sub = sub

    c = Comp.resolve()
    assert type(c.sub) == OtherComp


def test_subcomponent_cant_override_owner_type():
    class SubComp1(Component):
        pass

    class SubComp2(Component):
        pass

    class OtherComp(Component):
        par1 = 5
        sub: SubComp2

    class Comp(Component):
        def __init__(self, other: OtherComp, sub: SubComp1, par1=9):
            super().__init__()
            self.other = other
            self.sub = sub
            self.par1 = par1

    c = Comp.resolve()
    assert c.par1 == 9
    assert type(c.sub) == SubComp1


def test_cant_change_type_of_non_component_to_component():
    class SubComp(Component):
        pass

    class ParentComp(Component):
        def __init__(self, par1: int):
            self.par1 = par1

    class Comp(ParentComp):
        par1: SubComp

    with pytest.raises(TypeError):
        Comp.resolve()


def test_resolve_component_list():
    from typing import Tuple

    class SubComp1(Component):
        def __init__(self, par=42, par1: int = 3):
            self.par = par
            self.par1 = par1

    class SubComp2(Component):
        def __init__(self, par=9, par2: str = "Test"):
            self.par = par
            self.par2 = par2

    class Comp(Component):
        def __init__(self, components: Tuple[Component, ...]):
            self.components = components

    c = Comp.resolve()
    assert len(c.components) == 0

    class ParentComp(Comp):
        components: Tuple[SubComp1, SubComp2]

    c = ParentComp.resolve()
    assert len(c.components) == 2
    assert type(c.components[0]) == SubComp1 and c.components[0].par == 42 and c.components[0].par1 == 3
    assert type(c.components[1]) == SubComp2 and c.components[1].par == 9 and c.components[1].par2 == "Test"

    c = ParentComp.resolve(par1=5, par2="Hello", components_0_par=1, components_1_par=2)
    assert len(c.components) == 2
    assert type(c.components[0]) == SubComp1 and c.components[0].par == 1 and c.components[0].par1 == 5
    assert type(c.components[1]) == SubComp2 and c.components[1].par == 2 and c.components[1].par2 == "Hello"

    with pytest.raises(TypeError):
        kwargs = {'0_par': 1}
        ParentComp.resolve(**kwargs)

    with pytest.raises(TypeError):
        ParentComp.resolve(par=5)


def test_dont_override_param_with_function():
    class SubComp(Component):
        def __init__(self, key=42):
            self.key = key

    class Comp(Component):
        def par(self):
            return 3

        @property
        def key(self):
            return 9

        def __init__(self, sub: SubComp, par=5):
            self.sub = sub
            self.par = par

    c = Comp.resolve()
    assert c.par == 5 and c.sub.key == 42
