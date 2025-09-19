# Development Guide

## Setup Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/himakarreddy/1pass-env.git
   cd 1pass-env
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=onepass_env

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v
```

## Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

## Building and Publishing

1. Update version in `src/onepass_env/__about__.py`
2. Update CHANGELOG.md
3. Build the package:
   ```bash
   python -m build
   ```
4. Check the build:
   ```bash
   twine check dist/*
   ```
5. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

## Project Structure

```
1pass-env/
├── src/onepass_env/          # Main package
│   ├── __init__.py
│   ├── __about__.py          # Version info
│   ├── cli.py                # CLI interface
│   ├── core.py               # Core functionality
│   ├── onepassword.py        # 1Password integration
│   ├── exceptions.py         # Custom exceptions
│   └── config.py             # Configuration management
├── tests/                    # Test suite
├── docs/                     # Documentation
├── .github/workflows/        # CI/CD
├── pyproject.toml            # Project configuration
├── README.md
└── LICENSE
```
