import pytest


@pytest.fixture(scope="session")
def compat_assert_outcomes():
    """
    Use RunResult.assert_outcomes() in a way that's consistent across pytest
    versions.

    For more info, on how/why this is inconsistent between pytest versions:
    https://github.com/pytest-dev/pytest/issues/6505
    """

    def _compat_assert_outcomes(run_result, **kwargs):
        unplural = {
            'errors': 'error',
            'warnings': 'warning',
        }
        try:
            run_result.assert_outcomes(**kwargs)
        except TypeError:
            # Unpluralize the nouns and try again.
            run_result.assert_outcomes(**{
                unplural.get(key, key): val
                for key, val in kwargs.items()
            })

    return _compat_assert_outcomes


def test_funparam_basic(testdir):
    """Simple test of the base functionality."""

    # create a temporary pytest test module
    testdir.makepyfile(
        """
        def test_foo(funparam):
            @funparam
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
    result.assert_outcomes(
        failed=2,
        passed=2,
    )


def test_funparam_marks(testdir):
    testdir.makepyfile(
        """
        import pytest

        def test_addition(funparam):
            @funparam
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum_skipped = verify_sum.marks(pytest.mark.skip)

            verify_sum(1, 2, 3)
            verify_sum_skipped(2, 2, 5)
            verify_sum(4, 2, 6)
        """
    )

    result = testdir.runpytest()

    assert result.ret == 0

    result.assert_outcomes(
        skipped=1,
        passed=2,
    )


def test_funparam_does_not_die_from_fixtures(testdir):
    testdir.makepyfile(
        r"""
        def test_with_fixtures(capsys, funparam):

            @funparam
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
    result.assert_outcomes(
        failed=1,
        passed=2,
    )


def test_funparam_ids_default(testdir):
    testdir.makepyfile(
        r"""
        def test_sum(funparam):

            @funparam
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


def test_funparam_id_attribute(testdir):
    testdir.makepyfile(
        r"""
        def test_addition(funparam):
            @funparam
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum.id("one and two")(1, 2, 3)
            verify_sum.id("two and two")(2, 2, 5)
            verify_sum.id("four and two")(4, 2, 6)
        """
    )
    items, _ = testdir.inline_genitems()

    names = [item.name for item in items]
    # Should generate numbered args.
    assert names == [
        "test_addition[one and two]",
        "test_addition[two and two]",
        "test_addition[four and two]",
    ]


def test_funparam_in_fixture(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_sum(funparam):

            @funparam
            def verify_sum(a, b, c):
                assert a + b == c

            return verify_sum

        def test_foo(verify_sum):
            verify_sum(1, 2, 3)
            # This one fails
            verify_sum(2, 2, 3)
            verify_sum(2, 2, 4)
        """
    )
    result = testdir.runpytest()

    result.assert_outcomes(
        failed=1,
        passed=2,
    )


def test_funparam_nested_fixture(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_sum(funparam):

            @funparam
            def verify_sum(a, b, c):
                assert a + b == c

            return verify_sum

        @pytest.fixture
        def verify_nested1(verify_sum):
            return verify_sum

        @pytest.fixture
        def verify_nested(verify_nested1):
            return verify_nested1

        def test_foo(verify_nested):
            verify_nested(1, 2, 3)
            # This one fails
            verify_nested(2, 2, 3)
            verify_nested(2, 2, 4)
        """
    )
    result = testdir.runpytest()

    result.assert_outcomes(
        failed=1,
        passed=2,
    )


def test_funparam_multiple_functions(testdir):
    testdir.makepyfile(
        r"""
        def test_multiple(funparam):
            @funparam
            def verify_all_ints(*nums):
                for num in nums:
                    assert int(num) == num
            @funparam
            def verify_sum(a, b, c):
                assert a + b == c

            def verify_both(a, b, c):
                verify_all_ints(a, b, c)
                verify_sum(a, b, c)

            verify_both(1, 2, 3)
            # fails verify_all_ints
            verify_both("foo", "bar", "foobar")
            # fails verify_sum
            # verify_both(2, 2, 3)
        """
    )
    result = testdir.runpytest()

    result.assert_outcomes(
        failed=1,
        passed=3,
    )


def test_funparam_multiple_nested_fixtures(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_sum(funparam):

            @funparam
            def verify_sum(a, b, c):
                assert a + b == c

            return verify_sum

        @pytest.fixture
        def verify_both(verify_sum, funparam):

            @funparam
            def verify_all_ints(*nums):
                for num in nums:
                    assert int(num) == num

            def verify_both(a, b, c):
                verify_sum(a, b, c)
                verify_all_ints(a, b, c)

            return verify_both

        def test_foo(verify_both):
            verify_both(1, 2, 3)
            # fails verify_all_ints
            verify_both("foo", "bar", "foobar")
            # fails verify_sum
            # verify_both(2, 2, 3)
        """
    )
    result = testdir.runpytest()

    result.assert_outcomes(
        failed=1,
        passed=3,
    )


def test_funparam_collection_exception_in_unrelated_fixture(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def raise_error():
            raise Exception("OOPS!")

        @pytest.fixture
        def verify_sum(funparam, raise_error):

            @funparam
            def verify_sum(a, b, c):
                assert a + b == c

            return verify_sum

        def test_addition(verify_sum):
            verify_sum(1, 2, 3)
            verify_sum(2, 2, 3)
            verify_sum(2, 2, 4)
        """
    )

    items, _ = testdir.inline_genitems()
    # Should collect 3 items without trouble
    assert len(items) == 3


def test_funparam_nested_verifiers(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_stuff(funparam):

            @funparam
            def _verify_all_ints(*args):
                for arg in args:
                    assert int(arg) == arg

            @funparam
            def _verify_addition(a, b, c):
                assert a + b == c

            @funparam
            def _verify_stuff(a, b, c):
                _verify_all_ints(a, b, c)
                _verify_addition(a, b, c)

            return _verify_stuff

        def test_nested_verifiers(verify_stuff):
            verify_stuff(1, 2, 3)
            verify_stuff(2, 2, 3)
            verify_stuff("a", "b", "ab")
        """
    )
    result = testdir.runpytest()
    result.assert_outcomes(
        # Should fail the lot of them.
        failed=3,
    )
    result.stdout.fnmatch_lines(3 * [
        "*Cannot nest functions decorated with 'funparam'*",
    ])


def test_funparam_nonexistent_fixture(testdir, compat_assert_outcomes):
    testdir.makepyfile(
        r"""
        import pytest

        def test_nonexistent_fixture(funparam, bogus_fixture):

            @funparam
            def verify_addition(a, b, expected):
                assert a + b == expected

            verify_addition(1, 2, 3)
            verify_addition(2, 2, 4)
        """
    )
    result = testdir.runpytest()
    compat_assert_outcomes(result, errors=2)
    # Should complain about not finding the fixture.
    result.stdout.fnmatch_lines(2 * [
        "*fixture 'bogus_fixture' not found",
    ])


def test_parametrized_fixture(testdir):
    testdir.makepyfile("""\
        import pytest

        @pytest.fixture(params=[3, 7, 2.4])
        def number(request):
            return request.param

        def test_numbers(number, funparam):

            @funparam
            def verify_reversible(num1, num2):
                product = num1 * num2
                assert product / num2 == num1

            @funparam
            def verify_int(num):
                assert int(num) == num

            verify_reversible(number, 3)
            verify_reversible(3, number)
            verify_int(number)
    """)
    res = testdir.runpytest()
    # Should have parametrized properly
    res.assert_outcomes(passed=8, failed=1)


def test_parametrize_mark(testdir):
    testdir.makepyfile("""\
        import pytest

        @pytest.mark.parametrize('number', [3, 7, 2.4])
        def test_numbers(number, funparam):

            @funparam
            def verify_reversible(num1, num2):
                product = num1 * num2
                assert product / num2 == num1

            @funparam
            def verify_int(num):
                assert int(num) == num

            verify_reversible(number, 3)
            verify_reversible(3, number)
            verify_int(number)
    """)
    res = testdir.runpytest()
    res.assert_outcomes(passed=8, failed=1)


def test_clobbering_funparam(testdir):
    """
    This is probably a bad idea, but it works!
    """
    testdir.makepyfile("""\
        import pytest

        @pytest.fixture
        def funparam():
            return 42

        def test_it(funparam):
            assert funparam == 42
    """)
    res = testdir.runpytest()
    res.assert_outcomes(passed=1)
