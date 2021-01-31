# -*- coding: utf-8 -*-

import pytest
from unittest.mock import MagicMock
from functools import wraps


def generate_kwargs(definition, verifun):
    dry_run_kwargs = {}
    fixtureinfo = definition._fixtureinfo
    sought_names = fixtureinfo.argnames

    name2fixturedefs = fixtureinfo.name2fixturedefs
    for name in sought_names:
        fixture_def, *_ = name2fixturedefs[name]
        if name == "verifun":
            dry_run_kwargs["verifun"] = verifun
        elif "verifun" in fixture_def.argnames:
            kwargs = {
                key: MagicMock()
                for key in fixture_def.argnames
            }
            kwargs["verifun"] = verifun
            dry_run_kwargs[name] = fixture_def.func(**kwargs)
        else:
            dry_run_kwargs[name] = MagicMock()

    return dry_run_kwargs


def pytest_generate_tests(metafunc):
    # EARLY RETURN
    if "verifun" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return

    dry_run_verifun = GenerateTestsVerifun()

    # Can get FixtureDef from here?
    dry_run_kwargs = generate_kwargs(metafunc.definition, dry_run_verifun)

    test_function = metafunc.function

    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.

    test_function(**dry_run_kwargs)

    metafunc.parametrize(
        "_verifun_call_number",
        dry_run_verifun.generate_params()
    )


class AbstractVerifun:
    """
    The base API for the `verifun` fixture.

    verifun runs the test function multiple times, at different points in
    the pytest lifecycle. Each run has a different job, but the verifun object
    needs to work the same every time.
    """

    def __init__(self):
        self.verify_function = None
        self.ids = None

    def call_verify_function(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, verify_function=None, *, ids=None):
        if ids is not None:
            self.ids = ids

        # EARLY RETURN
        if verify_function is None:
            # Caller is most likely applying decorator like this:
            #   >>> @verifun()
            #   ... def verify_foo(): ...
            # Return the callable decorator so it can be used.
            return self

        self.verify_function = verify_function

        @wraps(verify_function)
        def verifun_wrapper(*args, **kwargs):
            return self.call_verify_function(*args, **kwargs)

        return verifun_wrapper


class GenerateTestsVerifun(AbstractVerifun):
    """
    The `verifun` fixture provided to the "dry run" test call during
    `pytest_generate_tests`.

    Record all calls to verify_function, but don't call the wrapped function.

    Generate test parameters based off `verifun` configuration and the recorded
    calls with `generate_params()`.
    """

    def __init__(self):
        self.calls = []
        super().__init__()

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


class RuntestVerifun(AbstractVerifun):
    """
    The `verifun` fixture provided to each run of the test function.

    Skips all calls to verify_function, except for when the current_call_number
    matches the _verifun_call_number (provided by the parametrized fixture.)
    """

    def __init__(self, _verifun_call_number):
        self._verifun_call_number = _verifun_call_number
        self.current_call_number = 0
        super().__init__()

    def call_verify_function(self, *args, **kwargs):
        try:
            if self.current_call_number == self._verifun_call_number:
                return self.verify_function(*args, **kwargs)
        finally:
            self.current_call_number += 1


@pytest.fixture
def verifun(_verifun_call_number):

    return RuntestVerifun(_verifun_call_number)
