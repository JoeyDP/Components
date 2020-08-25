import pytest

from components import Component
from components.param import Param, ComponentParam


@pytest.fixture()
def param():
    class OtherComp(Component):
        def __init__(self, par2=5):
            self.par2 = par2

    class OtherComp2(Component):
        def __init__(self, par3=42):
            self.par3 = par3

    class SubComp(Component):
        def __init__(self, sub1: OtherComp, sub2: OtherComp2, sub3: OtherComp, par1=3):
            self.sub1 = sub1
            self.sub2 = sub2
            self.sub3 = sub3
            self.par1 = par1

    class Comp(Component):
        def __init__(self, sub: SubComp):
            self.sub = sub

    params = Comp.get_requested_params()
    return ComponentParam("__main__", Comp, None, params=params)


def test_param_flatten(param):
    assert {x.name for x in param.flatten()} == {'par3', 'par2', 'par1'}

