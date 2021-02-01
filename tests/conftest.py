import pytest
from .fixtures.verify_examples import (  # noqa
    verify_examples, verify_one_example
)


pytest_plugins = 'pytester'


pytest.register_assert_rewrite(
    ".".join([__package__, "fixtures.verify_examples"])
)
