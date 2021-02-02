==============
pytest-verifun
==============

``pytest-verifun`` makes it easy to write parametrized tests.


Installation
------------

You can install "pytest-verifun" via `pip`_ from `PyPI`_::

    $ pip install pytest-verifun


Usage
-----

Inside a test function, decorate a function with the ``verifun`` fixture:

.. code-block:: python

    def test_addition(verifun):
        @verifun
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

        def test_addition(verifun):
            @verifun
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
    >       verify_sum(2, 2, 5)  # OOPS!

    test_readme.py:7: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    a = 2, b = 2, expected = 5
   
        @verifun
        def verify_sum(a, b, expected):
    >       assert a + b == expected
    E       assert (2 + 2) == 5

    test_readme.py:4: AssertionError
    ========================= 1 failed, 2 passed in 0.03s ==========================


The ``test_addition`` test case was split into 3 tests, one for each
``verify_sum`` call.

Because ``verifun`` is parametrizing the test calls, it even works with
commands like ``pytest --last-failed``::

    $ pytest --last-failed
    ============================= test session starts ==============================
    collected 1 item

    test_readme.py F                                                         [100%]

    =================================== FAILURES ===================================
    _______________________________ test_addition[1] _______________________________

        def test_addition(verifun):
            @verifun
            def verify_sum(a, b, expected):
                assert a + b == expected

            verify_sum(1, 2, 3)
    >       verify_sum(2, 2, 5)  # OOPS!

    test_readme.py:7: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    a = 2, b = 2, expected = 5
   
        @verifun
        def verify_sum(a, b, expected):
    >       assert a + b == expected
    E       assert (2 + 2) == 5

    test_readme.py:4: AssertionError
    ============================== 1 failed in 0.01s ===============================


To give each test case a pretty id, use the ``make_ids`` decorator attached to
a wrapped verifier function:

.. code-block:: python

    def test_addition(verifun):
        @verifun
        def verify_sum(a, b, expected):
            assert a + b == expected

        @verify_sum.make_ids
        def ids(a, b, expected):
            return f"{repr(a)} + {repr(b)} == {repr(expected)}"

        verify_sum(1, 2, 3)
        verify_sum(2, 2, 5)  # OOPS!
        verify_sum(4, 2, 6)

::

    $ pytest
    ============================= test session starts ==============================
    collected 3 items

    test_readme.py .F.                                                       [100%]

    =================================== FAILURES ===================================
    __________________________ test_addition[2 + 2 == 5] ___________________________

        def test_addition(verifun):
            @verifun
            def verify_sum(a, b, expected):
                assert a + b == expected

            @verify_sum.make_ids
            def ids(a, b, expected):
                return f"{repr(a)} + {repr(b)} == {repr(expected)}"

            verify_sum(1, 2, 3)
    >       verify_sum(2, 2, 5)  # OOPS!

    test_readme.py:11: 
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    a = 2, b = 2, expected = 5

        @verifun
        def verify_sum(a, b, expected):
    >       assert a + b == expected
    E       assert (2 + 2) == 5

    test_readme.py:4: AssertionError
    ========================= 1 failed, 2 passed in 0.02s ==========================


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-verifun" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/rjmill/pytest-verifun/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
