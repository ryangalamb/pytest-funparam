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
