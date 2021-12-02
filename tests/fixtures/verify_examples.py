"""
It's like doctest for pytest examples! Given a file with pytest code snippets
and sample output, verify that the code snippet runs a test with the expected
output.

Since this is specific to pytest-funparam, we can cut corners and make
assumptions that would be considered irresponsible under other circumstances.
"""


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
                    and not line.strip().startswith("$ ")
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
def verify_one_example(testdir, monkeypatch, capsys, run_mypy):
    # Use a consistent width for the terminal output.
    monkeypatch.setenv("COLUMNS", "80")

    def _verify_pytest(args, expected_output):
        result = testdir.runpytest(*args)
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

    def _verify_mypy(args, expected_output):
        stdout, *_ = run_mypy([str(testdir.tmpdir), *args])
        # Enforce an exact match, since there's not as much output as pytest.
        assert stdout.rstrip("\n") == expected_output.rstrip("\n")

    def _verify_one_example(code, *shell_blocks):
        testdir.makepyfile(code)
        for output in shell_blocks:
            command_line = output.splitlines()[0]
            cmd_tokens = shlex.split(command_line.lstrip("$ "))
            expected_output = "\n".join(output.splitlines()[1:])
            if cmd_tokens[0] == 'pytest':
                _verify_pytest(cmd_tokens[1:], expected_output)
            elif cmd_tokens[0] == 'mypy':
                _verify_mypy(cmd_tokens[1:], expected_output)
            else:
                pytest.fail(f"Unsupported command: {cmd_tokens[0]}")

    return _verify_one_example


@pytest.fixture
def verify_examples(verify_one_example):
    _skip_if_not_supported()

    def verify_examples(text):
        blocks = extract_blocks(text)

        last_python_block = None
        shell_blocks = []
        for block_type, block_text in blocks:
            if block_type == TYPE_PYTHON:
                if shell_blocks:
                    verify_one_example(last_python_block, *shell_blocks)
                last_python_block = block_text
                shell_blocks = []
                continue
            if last_python_block is not None:
                shell_blocks.append(block_text)
        if last_python_block and shell_blocks:
            verify_one_example(last_python_block, *shell_blocks)
    return verify_examples
