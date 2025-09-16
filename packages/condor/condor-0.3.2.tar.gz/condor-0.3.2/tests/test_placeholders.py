import pytest

import condor as co


class ComponentRaw(co.models.ModelTemplate):
    input = co.FreeField(co.Direction.input)
    output = co.AssignedField(co.Direction.output)

    x = placeholder(default=2.0)
    y = placeholder(default=1.0)

    output.z = x**2 + y


class ComponentImplementation(co.implementations.ExplicitSystem):
    pass


co.implementations.ComponentRaw = ComponentImplementation


class ComponentAsTemplate(co.ExplicitSystem, as_template=True):
    x = placeholder(default=2.0)
    y = placeholder(default=1.0)

    output.z = x**2 + y


@pytest.mark.parametrize("template", [ComponentRaw, ComponentAsTemplate])
class TestPlaceholders:
    def test_default_impl(self, template):
        class MyComp0(template):
            pass

        assert MyComp0().z == 5

    def test_new_io(self, template):
        class MyComp5(template):
            u = input()
            output.v = u**2 + 2 * u + 1

        out = MyComp5(3.0)
        assert out.z == 5
        assert out.v == 16

    def test_use_placeholders(self, template):
        class MyComp1(template):
            x = input()
            y = input()

        out = MyComp1(x=2.0, y=3.0)
        assert out.z == 7

    def test_partial_placeholder(self, template):
        class MyComp2(template):
            x = input()
            y = 3.0

        assert MyComp2(x=1.0).z == 1**2 + MyComp2.y

        # TODO currently this works, but probably shouldn't
        # keyword args x=..., y=... does fail
        assert MyComp2(3.0, 4.0).z == 3**2 + 3

    def test_override_placeholders(self, template):
        class MyComp3(template):
            x = 3.0
            y = 4.0

        assert MyComp3().z == 3**2 + 4

    def test_computed_placeholder(self, template):
        class MyComp4(template):
            u = input()
            x = u**0.5
            y = 0

            output.v = x + 5

        out = MyComp4(4.0)
        assert out.v == 4**0.5 + 5
        assert out.z == (4**0.5) ** 2 + 0
