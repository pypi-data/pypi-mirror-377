# Configen CLI

This is the CLI tool for **Configen**, built with **Typer**, **Rich**, and **OpenAI**.

### 1. Install/uninstall CLI from source code
```
pip install -e .
```
```
pip uninstall configen-cli
```

### 2. Install dependencies
```
poetry install
```

### 3. Deploy CLI to PyPI
```
poetry version patch
```
```
poetry build
```
```
poetry run twine upload --repository testpypi dist/* --verbose
```
```
poetry run twine upload --repository pypi dist/* --verbose
```