# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock
from functools import wraps


def pytest_generate_tests(metafunc):
    # EARLY RETURN
    if "verifun" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return
    m_verify_function = MagicMock()
    m_verifun = MagicMock(
        return_value=m_verify_function
    )

    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.
    metafunc.function(verifun=m_verifun)

    metafunc.parametrize(
        "_callnum",
        list(range(m_verify_function.call_count)),
    )


@pytest.fixture
def verifun(_callnum):

    current_call = 0

    def verifun_decorator(verify_function):
        nonlocal current_call

        @wraps(verify_function)
        def verifun_wrapper(*args, **kwargs):
            nonlocal current_call
            try:
                if current_call == _callnum:
                    return verify_function(*args, **kwargs)
            finally:
                current_call += 1

        return verifun_wrapper

    return verifun_decorator
