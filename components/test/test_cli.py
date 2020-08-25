import pytest

from components import Component
from components.cli import CLI


@pytest.fixture()
def cli():
    return CLI()


def test_command_is_component(cli):
    class Comp(Component, cli.Command):
        def run(self):
            pass

    with pytest.raises(TypeError):
        class Class(cli.Command):
            def run(self):
                pass


@pytest.mark.xfail
def test_provide_parameter(cli):
    assert False


@pytest.mark.xfail
def test_error_on_unknown_param(cli):
    assert False


@pytest.mark.xfail
def test_mandatory_param(cli):
    assert False


@pytest.mark.xfail
def test_optional_param(cli):
    assert False


@pytest.mark.xfail
def test_param_override_default_correct(cli):
    # attribute override should reflect new default
    assert False


@pytest.mark.xfail
def test_alias_of_param(cli):
    assert False


@pytest.mark.xfail
def test_snake_case_to_dashes(cli):
    assert False


@pytest.mark.xfail
def test_type_param_correct(cli):
    assert False


@pytest.mark.xfail
def test_boolean_param(cli):
    assert False


@pytest.mark.xfail
def test_list_param(cli):
    assert False


@pytest.mark.xfail
def test_multiple_commands(cli):
    assert False

