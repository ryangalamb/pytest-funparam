import pytest


def test_verifun_basic(testdir):
    """Simple test of the base functionality."""

    # create a temporary pytest test module
    testdir.makepyfile(
        """\
        def test_foo(verifun):
            @verifun
            def verify_foo(a, b, c):
                assert a + b == c

            verify_foo(1, 2, 3)

            # This one will fail
            verify_foo(2, 2, 3)

            verify_foo(2, 2, 4)

            # This one will fail
            verify_foo(2, 2, 5)
        """
    )

    result = testdir.runpytest()

    # Should have failed the test.
    assert result.ret == 1

    # Should have expanded the tests.
    assert result.parseoutcomes() == {
        "failed": 2,
        "passed": 2,
    }


def test_verifun_does_not_die_from_fixtures(testdir):
    testdir.makepyfile(
        r"""\
        def test_with_fixtures(capsys, verifun):

            @verifun
            def verify_with_fixtures(text):
                print(text)
                outerr = capsys.readouterr()
                assert outerr.out.rstrip("\n") == text

            verify_with_fixtures("foo")
            # This one will fail!
            verify_with_fixtures(3)
            verify_with_fixtures("bar")
        """
    )

    result = testdir.runpytest()

    # Should have failed the test.
    assert result.ret == 1

    # Should have expanded the tests.
    assert result.parseoutcomes() == {
        "failed": 1,
        "passed": 2,
    }


def test_verifun_ids_default(testdir):
    testdir.makepyfile(
        r"""\
        def test_sum(verifun):

            @verifun
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
            verify_sum(2, 2, 4)
            verify_sum(3, 10, 13)
        """
    )
    items, _ = testdir.inline_genitems()

    names = [item.name for item in items]
    # Should generate numbered args.
    assert names == [
        "test_sum[0]",
        "test_sum[1]",
        "test_sum[2]",
    ]


@pytest.mark.skip(reason="WIP")
def test_verifun_ids_override(testdir):
    testdir.makepyfile(
        r"""\
        def test_sum(verifun):
            def ids(a, b, expected):
                return f"{a} + {b} == {expected}"

            @verifun(ids=ids)
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
            verify_sum(2, 2, 4)
            verify_sum(3, 10, 13)
        """
    )
    items, _ = testdir.inline_genitems()

    names = [item.name for item in items]
    # Should use the ids function for identifiers.
    assert names == [
        "test_sum[1 + 2 == 3]",
        "test_sum[2 + 2 == 4]",
        "test_sum[3 + 10 == 13]",
    ]
