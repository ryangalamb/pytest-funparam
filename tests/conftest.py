import pytest
pytest_plugins = 'pytester'


pytest.register_assert_rewrite(
    ".".join([__package__, "fixtures.verify_examples"])
)


# ORDER MATTERS! This needs to get imported AFTER registering the assert
# rewriting, otherwise pytest can't rewrite the asserts.
from .fixtures.verify_examples import (  # noqa
    verify_examples, verify_one_example
)
