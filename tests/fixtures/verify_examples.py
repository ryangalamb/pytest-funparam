import pytest
from textwrap import dedent
import shlex


# This fixture is tightly coupled with output formats. Since these tests are
# more fragile than others, we should pin it to a specific version.
SUPPORTED_VERSIONS = ["6.2"]


def _skip_if_not_supported():
    for version in SUPPORTED_VERSIONS:
        supp_nums = version.split(".")
        found_nums = pytest.__version__.split(".")
        if found_nums[:len(supp_nums)] == supp_nums:
            return
    pytest.skip(
        "Documentation examples only supported on pytest versions: "
        + repr(SUPPORTED_VERSIONS)
    )


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
def verify_one_example(testdir, monkeypatch, capsys):
    # Use a consistent width for the terminal output.
    monkeypatch.setenv("COLUMNS", "80")

    def verify_one_example(code, *pytest_blocks):
        testdir.makepyfile(code)
        for output in pytest_blocks:
            command_line = output.splitlines()[0]
            cmd_tokens = shlex.split(command_line.lstrip("$ "))
            expected_output = "\n".join(output.splitlines()[1:])
            result = testdir.runpytest(*cmd_tokens[1:])
            expected_lines = expected_output.splitlines()
            summary, inline, timepart = expected_lines[-1].partition(" in ")
            # Replace the actual running time with a glob, so the test isn't
            # dependent on that.
            timepart = "*" + timepart[timepart.index("s"):]

            expected_lines[-1] = "".join([summary, inline, timepart])

            result.stdout.fnmatch_lines([
                line
                for line in expected_lines
                # Don't match empty lines. Those might be useful for matching.
                if line.strip() != ""
            ])
            capsys.readouterr()

    return verify_one_example


@pytest.fixture
def verify_examples(verify_one_example):
    _skip_if_not_supported()

    def verify_examples(text):
        blocks = extract_blocks(text)

        last_python_block = None
        pytest_blocks = []
        for block_type, block_text in blocks:
            if block_type == TYPE_PYTHON:
                if pytest_blocks:
                    verify_one_example(last_python_block, *pytest_blocks)
                last_python_block = block_text
                pytest_blocks = []
                continue
            if last_python_block is not None:
                pytest_blocks.append(block_text)
        if last_python_block and pytest_blocks:
            verify_one_example(last_python_block, *pytest_blocks)
    return verify_examples
