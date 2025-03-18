import unittest.mock

import pytest

from src.gag.rules import *
from src.gag.expr import *


class Contexts:
    class X(Var):
        y = Var()

        class Z(Var):
            class ZZ(Var):
                class A(Var):
                    _ = Var()

                a = A()

            _ = ZZ()

        z = Z()

    x = X()


x = Contexts.x


class X(RuleSet):
    def __init__(self):
        self.mock = unittest.mock.Mock()

    @rule(x)
    def on_x(self, *args, **kwargs):
        return self.mock.x(*args, **kwargs)

    @rule(x.y)
    def on_xy(self, *args, **kwargs):
        return self.mock.xy(*args, **kwargs)

    @rule(x.z)
    def on_xz(self, *args, **kwargs):
        return self.mock.xz(*args, **kwargs)

    @rule(x.z._.a)
    def on_xz_a(self, *args, **kwargs):
        return self.mock.xz_a(*args, **kwargs)

    @rule(x.z._.a._)
    def on_xz_a_(self, *args, **kwargs):
        return self.mock.xz_a_(*args, **kwargs)


@pytest.fixture
def sut():
    ret = X()
    for f in (ret.mock.x, ret.mock.xy, ret.mock.xz, ret.mock.xz_a, ret.mock.xz_a_):
        f.return_value = True
    return ret


def test_rules_pass(sut):
    assert sut.apply({"x": {"y": {}}})
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(),
        unittest.mock.call.xy(),
    ]


def test_rules_fail_at_start(sut):
    sut.mock.x.return_value = False
    assert not sut.apply({"x": {"y": {}}})
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(),
    ]


def test_rules_pass_for_unrelated(sut):
    assert sut.apply({"x": {"a": {}}})
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(),
    ]


def test_rules_fail_at_first_sibling(sut):
    sut.mock.xy.return_value = False
    sut.mock.xz.return_value = False
    assert not sut.apply({"x": {"y": {}, "z": {}}})
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(),
        unittest.mock.call.xy(),
    ]


def test_rules_pass_with_kwargs(sut):
    assert sut.apply({"x": {"y": {}}}, foo=1, bar=2)
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(foo=1, bar=2),
        unittest.mock.call.xy(foo=1, bar=2),
    ]


def test_rules_pass_with_one_placeholder(sut):
    assert sut.apply({"x": {"z": {"foo": {"a": {}}}}})
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(),
        unittest.mock.call.xz(),
        unittest.mock.call.xz_a("foo"),
    ]


def test_rules_pass_with_two_placeholders(sut):
    assert sut.apply({"x": {"z": {"foo": {"a": {"bar": {}}}}}})
    assert sut.mock.mock_calls == [
        unittest.mock.call.x(),
        unittest.mock.call.xz(),
        unittest.mock.call.xz_a("foo"),
        unittest.mock.call.xz_a_("foo", "bar"),
    ]
