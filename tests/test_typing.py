import pytest


def test_mypy_enforces_func_signature(assert_mypy_error_codes):
    assert_mypy_error_codes(
        """
        import pytest
        from pytest_funparam import FunparamFixture

        def test_addition(funparam: FunparamFixture):

            @funparam
            def verify_sum(a: int, b: int , expected: int):
                assert a + b == expected

            # These are valid
            verify_sum(1, 2, 3)
            verify_sum(2, 2, 4)
            verify_sum(2, 2, 9)

            # This be marked as invalid (since it's not an int)
            verify_sum(1, '2', 3)  # [arg-type]
        """,
    )


def test_mypy_allows_setting_marks(assert_mypy_error_codes):
    assert_mypy_error_codes(
        """
        import pytest
        from pytest_funparam import FunparamFixture

        def test_addition(funparam: FunparamFixture):

            @funparam
            def verify_sum(a: int, b: int , expected: int) -> None:
                assert a + b == expected

            verify_sum.marks(pytest.mark.skip)(1, 2, 3)
            verify_sum.marks(pytest.mark.skip())(1, 2, 3)
            verify_sum.marks(
                pytest.mark.skip,
                pytest.mark.foo,
            )(1, 2, 3)

            verify_sum.marks(pytest.mark.skip)(1, '2', 3)  # [arg-type]
        """,
    )


def test_mypy_allows_setting_id(assert_mypy_error_codes):
    assert_mypy_error_codes(
        """
        import pytest
        from pytest_funparam import FunparamFixture

        def test_addition(funparam: FunparamFixture):

            @funparam
            def verify_sum(a: int, b: int , expected: int) -> None:
                assert a + b == expected

            verify_sum.id('passes')(1, 2, 3)

            verify_sum.id('failing')(1, '2', 3)  # [arg-type]
        """,
    )


def test_mypy_forbids_double_id(assert_mypy_error_codes):
    assert_mypy_error_codes(
        """
        import pytest
        from pytest_funparam import FunparamFixture

        def test_addition(funparam: FunparamFixture):

            @funparam
            def verify_sum(a: int, b: int , expected: int) -> None:
                assert a + b == expected

            verify_sum.id('sanity check')
            verify_sum.marks(pytest.mark.skip).id('fine')

            verify_sum.id('one is fine').id('two is bad')  # [attr-defined]
            verify_sum.id('fine').marks(pytest.mark.skip).id('bad')  # [attr-defined]
        """,  # noqa
    )


def test_mypy_id_shorthand(assert_mypy_error_codes):
    assert_mypy_error_codes(
        """
        import pytest
        from pytest_funparam import FunparamFixture

        def test_addition(funparam: FunparamFixture):

            @funparam
            def verify_sum(a: int, b: int , expected: int) -> None:
                assert a + b == expected

            verify_sum['good'](1, 2, 3)

            verify_sum['bad args'](1, '2', 3)  # [arg-type]
            verify_sum['double id'].id('bad')  # [attr-defined]
            verify_sum.id('id then shorthand')['bad']  # [index]
        """,
    )


@pytest.mark.skip(reason="TODO")
def test_mypy_allows_setting_ids_in_decorator(assert_mypy_error_codes):
    assert_mypy_error_codes(
        """
        import pytest
        from pytest_funparam import FunparamFixture

        def test_addition(funparam: FunparamFixture):

            @funparam(ids=lambda a, b, c: f"{a!r} + {b!r} == {c!r}")
            def verify_sum(a: int, b: int , expected: int) -> None:
                assert a + b == expected

            verify_sum(1, 2, 3)

            verify_sum(1, '2', 3)  # [arg-type]
        """,
    )
