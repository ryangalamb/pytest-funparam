# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock
from inspect import signature
from functools import wraps, partial
from dataclasses import dataclass


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
        "_verifun_call_number",
        list(range(m_verify_function.call_count)),
    )


@dataclass
class Verifun:

    _verifun_call_number: int
    current_call: int = 0
    verify_function: callable = None
    ids: callable = None

    def __call__(self, verify_function=None, *, ids=None):
        if verify_function is None:
            return partial(self, ids=ids)

        self.verify_function = verify_function
        self.ids = ids

        @wraps(verify_function)
        def verifun_wrapper(*args, **kwargs):
            try:
                if self.current_call == self._verifun_call_number:
                    return self.verify_function(*args, **kwargs)
            finally:
                self.current_call += 1

        return verifun_wrapper


@pytest.fixture
def verifun(_verifun_call_number):

    return Verifun(_verifun_call_number)
