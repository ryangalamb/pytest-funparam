def test_verifun_basic(testdir):
    """Simple test of the base functionality."""

    # create a temporary pytest test module
    testdir.makepyfile(
        """
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


def test_verifun_marks(testdir):
    testdir.makepyfile(
        """
        import pytest

        def test_addition(verifun):
            @verifun
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
            verify_sum(2, 2, 5, _marks=pytest.mark.skip)
            verify_sum(4, 2, 6)
        """
    )

    result = testdir.runpytest()

    assert result.ret == 0

    assert result.parseoutcomes() == {
        "skipped": 1,
        "passed": 2,
    }


def test_verifun_does_not_die_from_fixtures(testdir):
    testdir.makepyfile(
        r"""
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
        r"""
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


def test_verifun_id_kwarg(testdir):
    testdir.makepyfile(
        r"""
        def test_addition(verifun):
            @verifun
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3, _id="one and two")
            verify_sum(2, 2, 5, _id="two and two")
            verify_sum(4, 2, 6, _id="four and two")
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


def test_verifun_in_fixture(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_sum(verifun):

            @verifun
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

    assert result.parseoutcomes() == {
        "failed": 1,
        "passed": 2,
    }


def test_verifun_nested_fixture(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_sum(verifun):

            @verifun
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

    assert result.parseoutcomes() == {
        "failed": 1,
        "passed": 2,
    }


def test_verifun_multiple_functions(testdir):
    testdir.makepyfile(
        r"""
        def test_multiple(verifun):
            @verifun
            def verify_all_ints(*nums):
                for num in nums:
                    assert int(num) == num
            @verifun
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

    assert result.parseoutcomes() == {
        "failed": 1,
        "passed": 3,
    }


def test_verifun_multiple_nested_fixtures(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def verify_sum(verifun):

            @verifun
            def verify_sum(a, b, c):
                assert a + b == c

            return verify_sum

        @pytest.fixture
        def verify_both(verify_sum, verifun):

            @verifun
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

    assert result.parseoutcomes() == {
        "failed": 1,
        "passed": 3,
    }


def test_verifun_collection_exception_in_unrelated_fixture(testdir):
    testdir.makepyfile(
        r"""
        import pytest

        @pytest.fixture
        def raise_error():
            raise Exception("OOPS!")

        @pytest.fixture
        def verify_sum(verifun, raise_error):

            @verifun
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
