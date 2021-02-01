from pathlib import Path


def test_readme(verify_examples):
    readme_path = Path(__file__).parent.parent / "README.rst"
    readme_text = readme_path.read_text()
    verify_examples(readme_text)
