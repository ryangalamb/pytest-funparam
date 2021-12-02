from textwrap import dedent


def test_verify_examples_simple(verify_examples):

    text = dedent(
        """\
        simple
        ======

        Given a simple example of a python code block:

        .. code-block:: python

            def test_sum(funparam):
                @funparam
                def verify_sum(a, b, expected):
                    assert a + b == expected

                verify_sum(1, 2, 3)
                verify_sum(2, 2, 3)  # OOPS!
                verify_sum(2, 2, 4)  # That's better


        And then a literal block starting with with ``$ pytest``::

            $ pytest
            ============================= test session starts ==============================
            collected 3 items

            test_verify_examples_simple.py .F.                                       [100%]

            =================================== FAILURES ===================================
            _________________________________ test_sum[1] __________________________________

                def test_sum(funparam):
                    @funparam
                    def verify_sum(a, b, expected):
                        assert a + b == expected

                    verify_sum(1, 2, 3)
            >       verify_sum(2, 2, 3)  # OOPS!

            test_verify_examples_simple.py:7: 
            _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

            a = 2, b = 2, expected = 3
           
                @funparam
                def verify_sum(a, b, expected):
            >       assert a + b == expected
            E       assert (2 + 2) == 3

            test_verify_examples_simple.py:4: AssertionError
            ========================= 1 failed, 2 passed in 0.03s ==========================
        """  # noqa
    )

    verify_examples(text)


def test_verify_examples_mypy(verify_examples):
    verify_examples(dedent(
        """\
        Given an example:

        .. code-block:: python

            def verify_sum(a: int, b: int, expected: int) -> None:
                assert a + b == expected

            verify_sum(1, 2, 3)
            verify_sum("a", "b", "ab")

        ::

            $ mypy
            test_verify_examples_mypy.py:5: error: Argument 1 to "verify_sum" has incompatible type "str"; expected "int"
            test_verify_examples_mypy.py:5: error: Argument 2 to "verify_sum" has incompatible type "str"; expected "int"
            test_verify_examples_mypy.py:5: error: Argument 3 to "verify_sum" has incompatible type "str"; expected "int"
            Found 3 errors in 1 file (checked 1 source file)
        """  # noqa
    ))
