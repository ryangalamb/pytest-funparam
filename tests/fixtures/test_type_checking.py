import pytest
from .type_checking import MypyLine, parse_mypy_line


def test_parse_mypy_line():
    line = '<string>:16: error: Argument 2 to "verify_sum" has incompatible type "str"; expected "int"  [arg-type]'  # noqa
    parsed = MypyLine(
        source='<string>',
        lineno=16,
        severity="error",
        message='Argument 2 to "verify_sum" has incompatible type "str"; expected "int"',  # noqa
        code='arg-type',
    )
    assert parse_mypy_line(line) == parsed


def test_assert_mypy_error_codes(assert_mypy_error_codes):
    # Happy path
    assert_mypy_error_codes(
        """
        foo: int
        foo = 3
        foo = 'bar'  # [assignment]
        """
    )
    # Expected failure did not happen
    with pytest.raises(AssertionError):
        assert_mypy_error_codes(
            """
            foo: int
            foo = 3  # [assigment]
            """
        )
    # Did not expect failure
    with pytest.raises(AssertionError):
        assert_mypy_error_codes(
            """
            foo: int
            foo = 'foo'
            """
        )
    # Wrong error expected
    with pytest.raises(AssertionError):
        assert_mypy_error_codes(
            """
            foo: int
            foo = 'foo'  # [arg-type]
            """
        )
