import pytest
from inspect import cleandoc
from mypy.api import run
from collections import namedtuple


MypyLine = namedtuple(
    'MypyLine',
    [
        'source',
        'lineno',
        'severity',
        'message',
        'code',
    ]
)


def parse_mypy_line(line):
    source, lineno, severity, raw_message = line.split(':')
    message, raw_error_code = raw_message.rsplit('[', 1)
    error_code = raw_error_code.rstrip("]")
    return MypyLine(
        source=source.strip(),
        lineno=int(lineno.strip()),
        severity=severity.strip(),
        message=message.strip(),
        code=error_code.strip(),
    )


@pytest.fixture
def run_mypy(tmp_path):
    config = tmp_path / "mypy.ini"
    config.write_text("[mypy]\n")

    def _run_mypy(args):
        return run([
            '--config-file', str(config),
            # mypy will complain about how older versions (< 6.x) of pytest
            # don't have type annotations. We're not concerned with that.
            '--ignore-missing-imports',
            *args,
        ])

    return _run_mypy


@pytest.fixture
def assert_mypy_error_codes(run_mypy):

    def _assert_mypy_error_codes(
        text,
        *,
        extra_args=(),
    ):
        text = cleandoc(text)
        output, _, returncode = run_mypy([
            "--no-error-summary",
            '--show-error-codes',
            *extra_args,
            "-c", text,
        ])
        expected_errors = {}
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "# [" not in line:
                continue
            _, code = line.rsplit("# [", 1)
            code = code.rstrip("]")
            expected_errors[lineno] = code

        actual_errors = {}
        for mypy_line in output.splitlines():
            parsed = parse_mypy_line(mypy_line)
            actual_errors[parsed.lineno] = parsed.code

        assert actual_errors == expected_errors, "\n".join([
            "mypy error codes did not match expected. Output:",
            output,
        ])

    return _assert_mypy_error_codes
