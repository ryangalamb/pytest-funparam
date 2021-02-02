import pytest
from unittest.mock import MagicMock
from functools import wraps, partial


def grab_mock_fixture_value(fixture_def, verifun, name2fixturedefs):
    if fixture_def.argname == "verifun":
        return verifun

    fixture_kwargs = {}
    for arg in fixture_def.argnames:
        try:
            inner_fixture_def, *_ = name2fixturedefs[arg]
        except KeyError:
            # The fixture's not defined yet, so we probably don't care.
            fixture_kwargs[arg] = MagicMock()
            continue
        found = grab_mock_fixture_value(
            inner_fixture_def,
            verifun,
            name2fixturedefs,
        )
        fixture_kwargs[arg] = found or MagicMock()

    return fixture_def.func(**fixture_kwargs)


def generate_kwargs(definition, verifun):
    dryrun_kwargs = {}
    fixtureinfo = definition._fixtureinfo
    sought_names = fixtureinfo.argnames

    name2fixturedefs = fixtureinfo.name2fixturedefs
    for name in sought_names:
        fixture_def, *_ = name2fixturedefs[name]
        found = grab_mock_fixture_value(fixture_def, verifun, name2fixturedefs)
        if found is None:
            dryrun_kwargs[name] = MagicMock()
        else:
            dryrun_kwargs[name] = found

    return dryrun_kwargs


def pytest_generate_tests(metafunc):
    # EARLY RETURN
    if "verifun" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return

    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.
    dryrun_verifun = GenerateTestsVerifun()

    kwargs = generate_kwargs(metafunc.definition, dryrun_verifun)

    metafunc.function(**kwargs)

    metafunc.parametrize(
        "_verifun_call_number",
        dryrun_verifun.generate_params()
    )


class AbstractVerifun:
    """
    The base API for the `verifun` fixture.

    verifun runs the test function multiple times, at different points in
    the pytest lifecycle. Each run has a different job, but the verifun object
    needs to work the same every time.
    """

    def __init__(self):
        self.verify_functions = {}
        self.ids_functions = {}

    def call_verify_function(
        self, key, *args, _marks=(), _id=None, **kwargs
    ):  # pragma: no cover
        raise NotImplementedError()

    def register_functions(self, verify_function, ids):
        key = id(verify_function)

        self.verify_functions[key] = verify_function
        self.ids_functions[key] = ids

        return key

    def __call__(self, verify_function=None, *, ids=None):
        # EARLY RETURN
        if verify_function is None:
            # Caller is most likely applying decorator like this:
            #   >>> @verifun()
            #   ... def verify_foo(): ...
            # Return the callable decorator so it can be used.
            return partial(self, ids=ids)

        key = self.register_functions(verify_function, ids)

        @wraps(verify_function)
        def verifun_wrapper(*args, **kwargs):
            return self.call_verify_function(key, *args, **kwargs)

        def make_ids(ids):
            """
            Set the ids_function for the wrapped verify_function.
            """
            self.ids_functions[key] = ids
            return ids

        verifun_wrapper.make_ids = make_ids

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

    def call_verify_function(self, key, *args, _marks=(), _id=None, **kwargs):
        self.calls.append((key, args, kwargs, _marks, _id))

    def generate_id(self, key, *args, **kwargs):
        ids = self.ids_functions[key]
        if ids is not None:
            return self.ids_functions[key](*args, **kwargs)
        return None

    def generate_params(self):
        params = []
        for callnum, call_args in enumerate(self.calls):
            key, args, kwargs, marks, id_ = call_args
            params.append(pytest.param(
                callnum,
                id=id_ or self.generate_id(key, *args, **kwargs),
                marks=marks,
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

    def call_verify_function(self, key, *args, _marks=(), _id=None, **kwargs):
        try:
            if self.current_call_number == self._verifun_call_number:
                return self.verify_functions[key](*args, **kwargs)
        finally:
            self.current_call_number += 1


@pytest.fixture
def verifun(_verifun_call_number):

    return RuntestVerifun(_verifun_call_number)
