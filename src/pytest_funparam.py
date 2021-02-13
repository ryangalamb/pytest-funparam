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


if TYPE_CHECKING:
    from _pytest.python import Metafunc, FunctionDefinition
    from _pytest.fixtures import FixtureDef
    from _pytest.mark import Mark, MarkDecorator, ParameterSet
    # This is from the type signature of `marks` kwarg for `pytest.param`.
    TYPE_MARKS = Union[MarkDecorator, Collection[Union[MarkDecorator, Mark]]]


# Sentinel value to mark an unrelated fixture.
_unrelated_fixture = object()


def grab_mock_fixture_value(
    fixture_def: "FixtureDef[Any]",
    funparam: "GenerateTestsFunparam",
    name2fixturedefs: Dict[str, Sequence["FixtureDef[Any]"]],
) -> Union[MagicMock, Any]:
    if fixture_def.argname == "funparam":
        return funparam

    fixture_kwargs = {}
    for arg in fixture_def.argnames:
        try:
            inner_fixture_def, *_ = name2fixturedefs[arg]
        except KeyError:
            # The fixture's not defined yet, so we probably don't care.
            fixture_kwargs[arg] = _unrelated_fixture
            continue
        found = grab_mock_fixture_value(
            inner_fixture_def,
            funparam,
            name2fixturedefs,
        )
        fixture_kwargs[arg] = found

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
    funparam: "GenerateTestsFunparam",
) -> Dict[str, Union[MagicMock, Any]]:
    dryrun_kwargs = {}
    fixtureinfo = definition._fixtureinfo
    sought_names = fixtureinfo.argnames

    name2fixturedefs = fixtureinfo.name2fixturedefs
    for name in sought_names:
        fixture_def, *_ = name2fixturedefs[name]
        found = grab_mock_fixture_value(
            fixture_def, funparam, name2fixturedefs
        )
        if found is _unrelated_fixture:
            dryrun_kwargs[name] = MagicMock()
        else:
            dryrun_kwargs[name] = found

    return dryrun_kwargs


def pytest_generate_tests(metafunc: "Metafunc") -> None:
    # EARLY RETURN
    if "funparam" not in metafunc.fixturenames:
        # Not interested in it, since our fixture isn't involved
        return

    # Call the test function with dummy fixtures to see how many times the
    # verify function is called.
    dryrun_funparam = GenerateTestsFunparam()

    kwargs = generate_kwargs(metafunc.definition, dryrun_funparam)

    metafunc.function(**kwargs)

    metafunc.parametrize(
        "_funparam_call_number",
        dryrun_funparam.generate_params()
    )


class AbstractFunparam:
    """
    The base API for the `funparam` fixture.

    funparam runs the test function multiple times, at different points in
    the pytest lifecycle. Each run has a different job, but the funparam object
    needs to work the same every time.
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


class GenerateTestsFunparam(AbstractFunparam):
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


class RuntestFunparam(AbstractFunparam):
    """
    The `funparam` fixture provided to each run of the test function.

    Skips all calls to verify_function, except for when the current_call_number
    matches the _funparam_call_number (provided by the parametrized fixture.)
    """

    def __init__(self, _funparam_call_number: int) -> None:
        self._funparam_call_number = _funparam_call_number
        self.current_call_number = 0
        super().__init__()

    def call_verify_function(
        self,
        key: int,
        *args: Any,
        _marks: "TYPE_MARKS" = (),
        _id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        try:
            if self.current_call_number == self._funparam_call_number:
                return self.verify_functions[key](*args, **kwargs)
        finally:
            self.current_call_number += 1


@pytest.fixture
def funparam(_funparam_call_number: int) -> AbstractFunparam:

    return RuntestFunparam(_funparam_call_number)
