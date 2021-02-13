===============
pytest-funparam
===============

``pytest-funparam`` makes it easy to write parametrized tests.


Installation
------------

You can install "pytest-funparam" via `pip`_ from `PyPI`_::

    $ pip install pytest-funparam


Usage
-----

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


Mark tests by using the ``_marks`` keyword argument on calls to verify:

.. code-block:: python

    import pytest

    def test_addition(funparam):
        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum(1, 2, 3)
        verify_sum(2, 2, 5, _marks=pytest.mark.skip)
        verify_sum(4, 2, 6)

::

    $ pytest
    ============================= test session starts ==============================
    collected 3 items

    test_readme.py .s.                                                       [100%]

    ========================= 2 passed, 1 skipped in 0.01s =========================


Note that the ``_marks`` keyword argument is passed through directly to the
``marks`` keyword argument of ``pytest.mark.param()``. This means the value can
be either a single mark or a collection of marks.

Similarly, add an ``id`` to a test using the ``_id`` keyword argument:

.. code-block:: python

    def test_addition(funparam):
        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum(1, 2, 3, _id="one and two")
        verify_sum(2, 2, 5, _id="two and two")
        verify_sum(4, 2, 6, _id="four and two")

::

    $ pytest --collect-only
    ============================= test session starts ==============================
    collected 3 items

    <Module test_readme.py>
      <Function test_addition[one and two]>
      <Function test_addition[two and two]>
      <Function test_addition[four and two]>

    ========================== 3 tests collected in 0.01s ==========================

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-funparam" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/rjmill/pytest-funparam/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
