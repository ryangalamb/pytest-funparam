import pytest
from pathlib import Path


pytestmark = pytest.mark.examples


def test_readme(verify_examples):
    readme_path = Path(__file__).parent.parent / "README.rst"
    readme_text = readme_path.read_text()
    verify_examples(readme_text)


def test_quirks(verify_examples):
    file_path = Path(__file__).parent.parent / "QUIRKS.rst"
    file_text = file_path.read_text()
    verify_examples(file_text)
