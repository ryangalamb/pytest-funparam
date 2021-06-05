import pytest
from unittest.mock import MagicMock
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Tuple,
    Union,
    List,
    Sequence,
    Collection,
    Callable,
    Optional,
)


if TYPE_CHECKING:  # pragma: no cover
    from _pytest.python import Metafunc, FunctionDefinition
    from _pytest.fixtures import FixtureDef
    from _pytest.mark import Mark, MarkDecorator, ParameterSet
    # This is from the type signature of `marks` kwarg for `pytest.param`.
    TYPE_MARKS = Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]]


class NotFunparam(Exception):
    """
    Signal that no funparam was found where we were looking.
    """


# Sentinel value to mark an unrelated fixture.
_unrelated_fixture = object()


def grab_mock_fixture_value(
    fixture_name: str,
    funparam_fixture: "GenerateTestsFunparam",
    name2fixturedefs: Dict[str, Sequence["FixtureDef[Any]"]],
) -> Union[MagicMock, Any]:
    try:
        *_, fixture_def = name2fixturedefs[fixture_name]
    except KeyError:
        # EARLY RETURN
        return _unrelated_fixture

    if fixture_def.argname == "funparam":
        # HACK: Ignore type because mypy doesn't recognize it as a wrapper.
        if fixture_def.func is funparam.__wrapped__:  # type: ignore
            return funparam_fixture
        else:
            return _unrelated_fixture

    fixture_kwargs = {
        arg: grab_mock_fixture_value(
            arg, funparam_fixture, name2fixturedefs
        )
        for arg in fixture_def.argnames
    }

    # EARLY RETURN
    if all(val is _unrelated_fixture for val in fixture_kwargs.values()):
        # None of these dependent fixtures use a funparam fixture. So this one
        # doesn't either!
        return _unrelated_fixture

    # Use MagicMocks to represent all the unrelated fixtures. Hopefully they
    # won't cause any heinous errors when we run this fixture.
    kwargs = {}
    for name, value in fixture_kwargs.items():
        if value is _unrelated_fixture:
            value = MagicMock()
        kwargs[name] = value

    return fixture_def.func(**kwargs)


def generate_kwargs(
    definition: "FunctionDefinition",
    funparam_fixture: "GenerateTestsFunparam",
) -> Dict[str, Union[MagicMock, Any]]:
    found_values = {}
    fixtureinfo = definition._fixtureinfo
    sought_names = fixtureinfo.argnames

    name2fixturedefs = fixtureinfo.name2fixturedefs
    for name in sought_names:
        found = grab_mock_fixture_value(
            name, funparam_fixture, name2fixturedefs
        )
        if found is not _unrelated_fixture:
            found_values[name] = found

    if found_values == {}:
        raise NotFunparam()

    dryrun_kwargs = {
        name: found_values.get(name) or MagicMock()
        for name in sought_names
    }

    return dryrun_kwargs


def pytest_generate_tests(metafunc: "Metafunc") -> None:
    # EARLY RETURN
    if "funparam" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return

    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.
    dryrun_funparam = GenerateTestsFunparam()

    try:
        kwargs = generate_kwargs(metafunc.definition, dryrun_funparam)
    except NotFunparam:
        return

    metafunc.function(**kwargs)

    metafunc.parametrize(
        "_funparam_call_number",
        dryrun_funparam.generate_params()
    )


class NestedFunparamError(Exception):
    """
    A 'funparam' function was called from within another 'funparam' function.

    'funparam' does a dry run of the test function to discover how many times
    'funparam' functions are called. It then generates that many parametrized
    test items.

    Because 'funparam' functions aren't actually called during the dry run, any
    calls from inside them will not be detected. 'funparam' cannot generate
    the right number test runs in these circumstances.
    """
    pass


class Funparam:
    """
    The base API for the `funparam` fixture.

    This is never instantiated directly, but it represents the common interface
    between all values of the `funparam` fixture. If you're looking for
    something to use in a type hint, this is it.
    """

    def __init__(self) -> None:
        self.verify_functions: Dict[int, Callable[..., None]] = {}

    def call_verify_function(
        self,
        key: int,
        *args: Any,
        _marks: "TYPE_MARKS" = (),
        _id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:  # pragma: no cover
        raise NotImplementedError()

    def _make_key(self, verify_function: Callable[..., None]) -> int:
        return id(verify_function)

    def __call__(
        self,
        verify_function: Callable[..., None]
    ) -> Callable[..., None]:
        key = self._make_key(verify_function)
        self.verify_functions[key] = verify_function

        @wraps(verify_function)
        def funparam_wrapper(*args: Any, **kwargs: Any) -> None:
            return self.call_verify_function(key, *args, **kwargs)

        return funparam_wrapper


class GenerateTestsFunparam(Funparam):
    """
    The `funparam` fixture provided to the "dry run" test call during
    `pytest_generate_tests`.

    Record all calls to verify_function, but don't call the wrapped function.

    Generate test parameters based off `funparam` configuration and the
    recorded calls with `generate_params()`.
    """

    def __init__(self) -> None:
        self.calls: List[
            Tuple[
                int,
                Sequence[Any],
                Dict[str, Any],
                "TYPE_MARKS",
                Optional[str],
            ]
        ] = []
        super().__init__()

    def call_verify_function(
        self,
        key: int,
        *args: Any,
        _marks: "TYPE_MARKS" = (),
        _id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.calls.append((key, args, kwargs, _marks, _id))

    def generate_params(self) -> Sequence["ParameterSet"]:
        params = []
        for callnum, call_args in enumerate(self.calls):
            key, args, kwargs, marks, id_ = call_args
            params.append(pytest.param(
                callnum,
                id=id_,
                marks=marks,
            ))
        return params


class RuntestFunparam(Funparam):
    """
    The `funparam` fixture provided to each run of the test function.

    Skips all calls to verify_function, except for when the current_call_number
    matches the _funparam_call_number (provided by the parametrized fixture.)
    """

    def __init__(self, _funparam_call_number: int) -> None:
        super().__init__()

        self._funparam_call_number = _funparam_call_number
        self.current_call_number = 0
        # Track when we're inside a call, so we can tell users not to nest
        # funparams.
        self._inside_call = False

    def call_verify_function(
        self,
        key: int,
        *args: Any,
        _marks: "TYPE_MARKS" = (),
        _id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if self._inside_call is True:
            raise NestedFunparamError(
                "Cannot nest functions decorated with 'funparam'."
            )
        try:
            if self.current_call_number == self._funparam_call_number:
                self._inside_call = True
                return self.verify_functions[key](*args, **kwargs)
        finally:
            self.current_call_number += 1
            self._inside_call = False


@pytest.fixture
def funparam(_funparam_call_number: int) -> Funparam:
    return RuntestFunparam(_funparam_call_number)
