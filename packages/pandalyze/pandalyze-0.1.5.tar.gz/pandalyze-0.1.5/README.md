# pandalyze

Lightweight utilities to inspect and analyze pandas.

Features
- Quick memory and performance insights for DataFrames
- Human-friendly console output using rich

Installation

Install from PyPI (after release):

	pip install pandalyze

Or install from source for development:

	python -m venv .venv
	source .venv/bin/activate
	pip install -e .

Basic usage

```python
from pandalyze import analyze

# Example: analyze your function stats
@analyze
def your_function()
    pass
```

Publishing

- This project uses `pyproject.toml` with Poetry-compatible build back-end (`poetry-core`).
- Bump the `version` in `pyproject.toml` before publishing to PyPI/TestPyPI.

Contributing

Contributions are welcome. Open issues or pull requests and follow standard GitHub workflow.

License

Specify a license in `pyproject.toml` and add a `LICENSE` file if you want this released publicly.

