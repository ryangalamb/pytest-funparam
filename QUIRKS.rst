======
Quirks
======

This is a collection of the potentially surprising aspects of
``pytest-funparam``.

Requesting ``funparam`` but not using it
----------------------------------------

If you request the ``funparam`` fixture in a test that isn't calling a
``funparam``-decorated function, the test will be skipped!

It's equivalent to parametrizing a test case without passing any parameters to
it.

.. code-block:: python

    def test_addition(funparam):

        # OOPS! We forgot to decorate the function here!
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum(1, 2, 3)
        verify_sum(4, 2, 6)


This won't run any tests::

    $ pytest
    ============================= test session starts ==============================
    collected 1 item

    test_quirks.py s                                                         [100%]

    ============================== 1 skipped in 0.01s ==============================


Other fixtures named ``funparam``
---------------------------------

First off, it's probably not a great idea to rely on this behavior. I'm
documenting it here because it might be helpful for understanding
``pytest-funparam``.


.. code-block:: python

    import pytest


    @pytest.fixture
    def funparam():
        return 42


    def test_it(funparam):
        assert funparam == 42


``pytest-funparam`` will recognize that the ``funparam`` fixture is not THE
``funparam`` fixture. And it won't do anything special::

    $ pytest
    ============================= test session starts ==============================
    collected 1 item

    test_quirks.py .                                                         [100%]

    ============================== 1 passed in 0.01s ===============================


**This is where things get silly.** If you try to "request" ``funparam`` from
within another fixture called ``funparam``:

.. code-block:: python
    import pytest


    @pytest.fixture
    def funparam(funparam):

        def _funparam(func):
            return funparam(func)

        return _funparam


    def test_addition(funparam):

        @funparam
        def verify_sum(a, b, expected):
            assert a + b == expected

        verify_sum(3, 4, 7)
        verify_sum(3, 4, 8)


**It does not work!** It complains about not having a
``_funparam_call_number``::

    $ pytest
    ============================= test session starts ==============================
    collected 1 item

    test_quirks.py E                                                         [100%]

    ==================================== ERRORS ====================================
    _______________________ ERROR at setup of test_addition ________________________
    file */test_quirks.py, line 13
      def test_addition(funparam):
    file */test_quirks.py, line 4
      @pytest.fixture
      def funparam(funparam):

    file */pytest_funparam/__init__.py, line *
      @pytest.fixture
      def funparam(_funparam_call_number: int) -> Funparam:
    E       fixture '_funparam_call_number' not found

    >       available fixtures: *
    >       use 'pytest --fixtures [testpath]' for help on them.

    */pytest_funparam/__init__.py:266
    =========================== short test summary info ============================
    ERROR test_quirks.py::test_addition
    =============================== 1 error in 0.02s ===============================

``_funparam_call_number`` is the parameter that's used to tell ``funparam``
which of the decorated function calls to run. During the
``pytest_generate_tests`` hook, that ``funparam`` fixture was marked as
"unrelated" because it's not the one supplied by ``pytest-funparam``.

This case might be possible to support in the future, but I'd rather not make
the "fixture dry run" more convoluted than it already is. For now, the
safest/easiest solution is to let it fail loudly and document how/why it's
happening.
