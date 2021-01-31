# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock
from inspect import signature
from functools import wraps


def pytest_generate_tests(metafunc):
    # EARLY RETURN
    if "verifun" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return
    m_verify_function = MagicMock()

    test_function = metafunc.function

    sig = signature(test_function)
    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.
    dry_run_kwargs = {
        argname: MagicMock()
        for argname in sig.parameters.keys()
    }

    dry_run_kwargs["verifun"].return_value = m_verify_function

    test_function(**dry_run_kwargs)

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
