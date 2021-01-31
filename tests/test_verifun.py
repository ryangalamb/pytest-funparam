import pytest


def test_verifun_simple(testdir):
    """Make sure that pytest accepts our fixture."""

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
