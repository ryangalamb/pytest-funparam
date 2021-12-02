===============
pytest-funparam
===============

``pytest-funparam`` makes it easy to write parametrized tests.

Unlike ``pytest.mark.parametrize``, ``pytest-funparam``:

* includes the failing parameter in pytest tracebacks;
* enables static type checking of parameters; and
* keeps parameters and assertions closer together.

.. contents::


Installation
============

You can install "pytest-funparam" via `pip`_ from `PyPI`_::

    $ pip install pytest-funparam


Usage
=====

Inside a test function, decorate a function with the ``funparam`` fixture:

.. code-block:: python

    def test_addition(funparam):
        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum(1, 2, 3)
        verify_sum(2, 2, 5)  # OOPS!
        verify_sum(4, 2, 6)


And run pytest::

    $ pytest
    ============================= test session starts ==============================
    collected 3 items

    test_readme.py .F.                                                       [100%]

    =================================== FAILURES ===================================
    _______________________________ test_addition[1] _______________________________

        def test_addition(funparam):
            @funparam
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
    >       verify_sum(2, 2, 5)  # OOPS!

    test_readme.py:7: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    a = 2, b = 2, expected = 5
   
        @funparam
        def verify_sum(a, b, expected):
    >       assert a + b == expected
    E       assert (2 + 2) == 5

    test_readme.py:4: AssertionError
    ========================= 1 failed, 2 passed in 0.03s ==========================


The ``test_addition`` test case was split into 3 tests, one for each
``verify_sum`` call.

Because ``funparam`` is parametrizing the test calls, it even works with
commands like ``pytest --last-failed``::

    $ pytest --last-failed
    ============================= test session starts ==============================
    collected 1 item

    test_readme.py F                                                         [100%]

    =================================== FAILURES ===================================
    _______________________________ test_addition[1] _______________________________

        def test_addition(funparam):
            @funparam
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
    >       verify_sum(2, 2, 5)  # OOPS!

    test_readme.py:7: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    a = 2, b = 2, expected = 5
   
        @funparam
        def verify_sum(a, b, expected):
    >       assert a + b == expected
    E       assert (2 + 2) == 5

    test_readme.py:4: AssertionError
    ============================== 1 failed in 0.01s ===============================


Markers
-------

Mark tests by using the ``.marks()`` method of your funparam function.

.. code-block:: python

    import pytest

    def test_addition(funparam):
        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum(1, 2, 3)
        verify_sum.marks(pytest.mark.skip)(2, 2, 5)
        verify_sum(4, 2, 6)

::

    $ pytest
    ============================= test session starts ==============================
    collected 3 items

    test_readme.py .s.                                                       [100%]

    ========================= 2 passed, 1 skipped in 0.01s =========================


Test IDs
--------

Similarly, add an ``id`` to a test using the ``.id()`` method of your funparam
function:

.. code-block:: python

    def test_addition(funparam):
        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum.id("one and two")(1, 2, 3)
        verify_sum.id("two and two")(2, 2, 5)
        verify_sum.id("four and two")(4, 2, 6)

::

    $ pytest --collect-only
    ============================= test session starts ==============================
    collected 3 items

    <Module test_readme.py>
      <Function test_addition[one and two]>
      <Function test_addition[two and two]>
      <Function test_addition[four and two]>

    ========================== 3 tests collected in 0.01s ==========================


You can also use the shorthand for assigning an ``id``. (It does the same thing
as calling ``.id()``.)

.. code-block:: python

    def test_addition(funparam):
        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum["one and two"](1, 2, 3)
        verify_sum["two and two"](2, 2, 5)
        verify_sum["four and two"](4, 2, 6)

::

    $ pytest --collect-only
    ============================= test session starts ==============================
    collected 3 items

    <Module test_readme.py>
      <Function test_addition[one and two]>
      <Function test_addition[two and two]>
      <Function test_addition[four and two]>

    ========================== 3 tests collected in 0.01s ==========================


Type Annotations
----------------

``pytest-funparam`` has full type annotations. The ``funparam`` fixture returns
a ``FunparamFixture`` object. You can import it from ``pytest_funparam``:

.. code-block:: python

    import pytest
    from pytest_funparam import FunparamFixture

    def test_addition(funparam: FunparamFixture):

        @funparam
        def verify_sum(a: int, b: int , expected: int):
            assert a + b == expected

        # These are valid
        verify_sum(1, 2, 3)
        verify_sum['it accommodates ids'](2, 2, 4)
        # Marks work too!
        verify_sum.marks(pytest.mark.xfail)(2, 2, 9)

        # This will be marked as invalid (since it's not an int)
        verify_sum(1, '2', 3)

        # Using id/marks will still preserve the function's typing.
        verify_sum['should be an int'](1, 2, '3')

::

    $ mypy
    test_readme.py:17: error: Argument 2 to "verify_sum" has incompatible type "str"; expected "int"
    test_readme.py:20: error: Argument 3 to "verify_sum" has incompatible type "str"; expected "int"
    Found 2 errors in 1 file (checked 1 source file)


License
=======

Distributed under the terms of the `MIT`_ license, "pytest-funparam" is free and open source software


Issues
======

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/rjmill/pytest-funparam/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
