# -*- coding: utf-8 -*-

import pytest
from functools import wraps


@pytest.fixture
def verifun():
    def verifun_decorator(verify_function):

        @wraps(verify_function)
        def verifun_wrapper(*args, **kwargs):
            return verify_function(*args, **kwargs)

        return verifun_wrapper

    return verifun_decorator
