# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock
from inspect import signature
from functools import wraps
from dataclasses import dataclass, field


def pytest_generate_tests(metafunc):
    # EARLY RETURN
    if "verifun" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return

    test_function = metafunc.function

    sig = signature(test_function)
    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.
    dry_run_kwargs = {
        argname: MagicMock()
        for argname in sig.parameters.keys()
    }

    dry_run_verifun = DryRunVerifun()

    dry_run_kwargs["verifun"] = dry_run_verifun

    test_function(**dry_run_kwargs)

    metafunc.parametrize(
        "_verifun_call_number",
        dry_run_verifun.generate_params()
    )


@dataclass
class Verifun:

    _verifun_call_number: int = None
    current_call: int = 0
    verify_function: callable = None
    ids: callable = None

    def call_verify_function(self, *args, **kwargs):
        try:
            if self.current_call == self._verifun_call_number:
                return self.verify_function(*args, **kwargs)
        finally:
            self.current_call += 1

    def set_verify(self, verify_function):
        self.verify_function = verify_function

    def set_ids(self, ids):
        self.ids = ids

    def __call__(self, verify_function=None, *, ids=None):
        if ids is not None:
            self.set_ids(ids)

        if verify_function is None:
            # Doing something like so:
            #   >>> @verifun()
            #   ... def verify_foo(): ...
            return self

        self.set_verify(verify_function)

        @wraps(verify_function)
        def verifun_wrapper(*args, **kwargs):
            return self.call_verify_function(*args, **kwargs)

        return verifun_wrapper


@dataclass
class DryRunVerifun(Verifun):

    calls: list = field(default_factory=list)

    def call_verify_function(self, *args, **kwargs):
        self.calls.append((args, kwargs))

    def generate_params(self):
        if self.ids is None:
            return list(range(len(self.calls)))

        params = []
        for callnum, call_args in enumerate(self.calls):
            args, kwargs = call_args
            params.append(pytest.param(
                callnum,
                id=self.ids(*args, **kwargs)
            ))
        return params


@pytest.fixture
def verifun(_verifun_call_number):

    return Verifun(_verifun_call_number)
