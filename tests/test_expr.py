import pytest

from src.gag.expr import *
import unittest.mock


@pytest.fixture(autouse=True)
def reset_ref_expr_store():
    # Reset the store before each test
    RefExpr._store.clear()


def test_ops():
    a = RefExpr("a")
    b = RefExpr("b")
    c = RefExpr("c")

    assert instantiate(a | (b & c)) == "${{ a || b && c }}"
    assert instantiate((a | b) & c) == "${{ (a || b) && c }}"
    assert instantiate(~a | b) == "${{ !a || b }}"
    assert instantiate(~(a | b)) == "${{ !(a || b) }}"
    assert instantiate((a & b)[0]) == "${{ (a && b)[0] }}"
    assert instantiate((a & b).x) == "${{ (a && b).x }}"
    assert instantiate((a == b) | (a < c)) == "${{ a == b || a < c }}"
    assert (
        instantiate((0 != a) & (a >= c) & (b > c)) == "${{ a != 0 && a >= c && b > c }}"
    )


def test_reftree():
    a = RefExpr("a")
    b = RefExpr("b")
    c = RefExpr("c")

    assert reftree(a) == {"a": {}}
    assert reftree(a | (b & c)) == dict.fromkeys("abc", {})
    assert reftree(~(a | b) & a) == dict.fromkeys("ab", {})
    assert reftree(a[b][0]) == dict.fromkeys("ab", {})


def test_reftree_on_strings():
    a = RefExpr("a")
    b = RefExpr("b")
    c = RefExpr("c")

    assert reftree(f"-- {a} __ {b} || {c} >>") == dict.fromkeys("abc", {})
    assert reftree(
        {
            "FOO": f"/{a}",
            f"<{b}>": f"/{a}",
            "BAZ": [c],
        }
    ) == dict.fromkeys("abc", {})
    assert reftree([f"<{a}>", f"<{a}, {b}>", {"A": "a", "c": c}]) == dict.fromkeys(
        "abc", {}
    )


def test_no_bool():
    error_handler = unittest.mock.Mock()
    with on_error(error_handler):
        a = RefExpr("a")
        assert a
        error_handler.assert_called_once()


def test_simple_context():
    @contexts
    class Contexts:
        class X(RefExpr):
            b: RefExpr
            a: RefExpr

        x: X

    x = Contexts.x

    assert instantiate(x) == "${{ x }}"
    assert instantiate(x.a) == "${{ x.a }}"
    assert instantiate(x.b) == "${{ x.b }}"
    assert instantiate(x._) == "${{ x.* }}"

    error_handler = unittest.mock.Mock()
    with on_error(error_handler):
        _ = x.c
        _ = x.b.whatever
        error_handler.assert_has_calls(
            [
                unittest.mock.call("`c` not available in `x`"),
                unittest.mock.call("`whatever` not available in `x.b`"),
            ]
        )


def test_context_with_call_operator():
    m = unittest.mock.Mock()

    @contexts
    class Contexts:
        class X(RefExpr):
            a: RefExpr
            b: RefExpr

        x: X

    x = Contexts.x
    x._make_callable(m)
    x(1, 2, 3, a=4, b=5)
    assert m.mock_calls == [unittest.mock.call(1, 2, 3, a=4, b=5)]


def test_nested_context():
    @contexts
    class Contexts:
        class X(RefExpr):
            a: RefExpr
            b: RefExpr

            class Y(RefExpr):
                c: RefExpr
                d: RefExpr

            y: Y

        x: X

    x = Contexts.x

    assert instantiate(x.a) == "${{ x.a }}"
    assert instantiate(x.b) == "${{ x.b }}"
    assert instantiate(x.y.c) == "${{ x.y.c }}"
    assert instantiate(x.y.d) == "${{ x.y.d }}"

    error_handler = unittest.mock.Mock()
    with on_error(error_handler):
        _ = x.c
        _ = x.y.bla
        _ = x.y.a
        error_handler.assert_has_calls(
            [
                unittest.mock.call("`c` not available in `x`"),
                unittest.mock.call("`bla` not available in `x.y`"),
                unittest.mock.call("`a` not available in `x.y`"),
            ]
        )


def test_map_context():
    @contexts
    class Contexts:
        class X(RefExpr):
            a: RefExpr
            b: FlatMap

            class Y(RefExpr):
                foo: RefExpr
                bar: RefExpr

            __getattr__: Map[Y]

        x: X

    x = Contexts.x

    assert instantiate(x) == "${{ x }}"
    assert instantiate(x.a) == "${{ x.a }}"
    assert instantiate(x.b) == "${{ x.b }}"
    assert instantiate(x.b.whatever) == "${{ x.b.whatever }}"
    assert instantiate(x.baz) == "${{ x.baz }}"
    assert instantiate(x.baz.foo) == "${{ x.baz.foo }}"
    assert instantiate(x.baz.bar) == "${{ x.baz.bar }}"
    assert instantiate(x._.foo) == "${{ x.*.foo }}"

    assert reftree(x.a & x.baz.foo & x._.bar) == {
        "x": {"a": {}, "baz": {"foo": {}}, "*": {"bar": {}}}
    }

    error_handler = unittest.mock.Mock()
    with on_error(error_handler):
        _ = x.b.foo.whatever
        _ = x.baz.foo.whatever
        _ = x.baz.bar.whatever
        _ = x._.whatever
        error_handler.assert_has_calls(
            [
                unittest.mock.call("`whatever` not available in `x.b.foo`"),
                unittest.mock.call("`whatever` not available in `x.baz.foo`"),
                unittest.mock.call("`whatever` not available in `x.baz.bar`"),
                unittest.mock.call("`whatever` not available in `x.*`"),
            ]
        )


def test_functions():
    f = function("foo", 3)
    x = RefExpr("x")
    assert instantiate(f(1, x, "s's")) == "${{ foo(1, x, 's''s') }}"
    for wrong, expected_error in (
        (lambda: f(1), "wrong number of arguments to `foo`, expected 3, got 1"),
        (
            lambda: f(1, 2, 3, 4),
            "wrong number of arguments to `foo`, expected 3, got 4",
        ),
        (
            lambda: f(x=1, y=2, z=3),
            "unexpected keyword arguments to `foo`, expected 3 positional arguments",
        ),
    ):
        error_handler = unittest.mock.Mock()
        with on_error(error_handler):
            call = wrong()
            error_handler.assert_called_once_with(expected_error)
            assert instantiate(call) == f"${{{{ error('{expected_error}') }}}}"

    assert reftree(f(1, x, "s's")) == {"x": {}}


def test_error_expr():
    error_handler = unittest.mock.Mock()
    with on_error(error_handler):
        e = ErrorExpr("an error")
        error_handler.assert_not_called()
        assert instantiate(e) == "${{ error('an error') }}"
        error_handler.assert_called_once_with("an error")
        error_handler.reset_mock()
        assert instantiate(e.x.y[0] & 3 | True == "x") == "${{ error('an error') }}"
        error_handler.assert_not_called()


def test_default_error():
    with pytest.raises(ValueError) as e:
        _ = ~ErrorExpr("an error")
    assert e.value.args == ("an error",)
