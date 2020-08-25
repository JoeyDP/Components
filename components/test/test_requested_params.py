import pytest

from components import Component



def test_subcomponent_shadowed_param_name():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub: SubComp, key=3):
            self.sub = sub
            self.key = key

    assert SubComp.get_requested_params()[0].aliases == {'key'}
    assert Comp.get_requested_params()[0].params[0].aliases == {'sub_key'}
    assert Comp.get_requested_params()[1].aliases == {'key'}


def test_subcomponent_conflicting_param_names():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub1: SubComp, sub2: SubComp):
            self.sub1 = sub1
            self.sub2 = sub2

    assert SubComp.get_requested_params()[0].aliases == {'key'}
    assert Comp.get_requested_params()[0].params[0].aliases == {'sub1_key'}
    assert Comp.get_requested_params()[1].params[0].aliases == {'sub2_key'}


def test_subcomponent_3_conflicting_param_names():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub1: SubComp, sub2: SubComp, sub3: SubComp):
            self.sub1 = sub1
            self.sub2 = sub2
            self.sub3 = sub3

    assert SubComp.get_requested_params()[0].aliases == {'key'}
    assert Comp.get_requested_params()[0].params[0].aliases == {'sub1_key'}
    assert Comp.get_requested_params()[1].params[0].aliases == {'sub2_key'}
    assert Comp.get_requested_params()[2].params[0].aliases == {'sub3_key'}


def test_subcomponent_impossible_param_name():
    class SubComp(Component):
        def __init__(self, key=5):
            self.key = key

    class Comp(Component):
        def __init__(self, sub1: SubComp, sub2: SubComp, sub1_key=42):
            self.sub1 = sub1
            self.sub2 = sub2
            self.sub1_key = sub1_key

    with pytest.raises(AttributeError):
        Comp.get_requested_params()


# def test_type_override_correct_params():
#     class SubComp(Component):
#         def __init__(self, par1=3):
#             self.par1 = par1
#
#     class OtherComp(Component):
#         def __init__(self, par2=5):
#             self.par2 = par2
#
#     class Comp(Component):
#         sub: OtherComp
#
#         def __init__(self, sub: SubComp):
#             self.sub = sub
#
#     params = Comp.get_requested_params()
