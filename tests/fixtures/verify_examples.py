import pytest
from textwrap import dedent


TYPE_PYTHON = "python"
TYPE_OUTPUT = "output"


def extract_blocks(rst_text):
    """
    Given string rst text, extracts the python code blocks and literal blocks,
    returning them in a list.
    """
    all_examples = []
    current_type = None
    current_example = None
    for line in rst_text.splitlines():
        if current_type is not None:
            if current_example == []:
                if line.strip() == "":
                    continue
                if not line.startswith('  '):
                    # Not actually a block. Skip it.
                    current_type = None
                    current_example = None
                    continue
                if (
                    current_type == TYPE_OUTPUT
                    and not line.strip().startswith("$ pytest")
                ):
                    # Not something we care about. ditch it.
                    current_type = None
                    current_example = None
                    continue

            if not (
                line.strip() == ""
                or line.startswith("  ")
            ):
                all_examples.append((current_type, current_example))
                current_type = None
                current_example = None
            else:
                current_example.append(line)
                continue

        if " ".join(line.split()) == ".. code-block:: python":
            current_type = TYPE_PYTHON
            current_example = []
        elif line.strip().endswith("::"):
            current_type = TYPE_OUTPUT
            current_example = []

    if current_example:
        all_examples.append((current_type, current_example))

    all_example_texts = []

    for example_type, example_lines in all_examples:
        while example_lines and example_lines[-1].strip() == "":
            example_lines.pop()

        example_text = dedent("\n".join(example_lines))
        all_example_texts.append((example_type, example_text))
    return all_example_texts


@pytest.fixture
def verify_one_example(testdir):
    def verify_one_example(code, output):
        # command_line = output.splitlines()[0]
        expected_output = "\n".join(output.splitlines()[1:])
        testdir.makepyfile(code)
        testdir.makeini(dedent(
            """\
            [pytest]
            console_output_style = classic
            """
        ))
        result = testdir.runpytest()
        expected_lines = expected_output.splitlines()
        summary, inline, timepart = expected_lines[-1].partition(" in ")
        # Replace the actual runtime with a glob, so the test isn't dependent
        # on that.
        timepart = "*" + timepart[timepart.index("s"):]

        expected_lines[-1] = "".join([summary, inline, timepart])

        result.stdout.fnmatch_lines([
            line
            for line in expected_lines
            # Don't match empty lines. Those might be useful for matching.
            if line.strip() != ""
        ])

    return verify_one_example


@pytest.fixture
def verify_examples(verify_one_example):

    def verify_examples(text):
        blocks = extract_blocks(text)

        last_python_block = None
        for block_type, block_text in blocks:
            if block_type == TYPE_PYTHON:
                last_python_block = block_text
                continue
            if last_python_block is not None:
                verify_one_example(last_python_block, block_text)
            last_python_block = None
    return verify_examples
