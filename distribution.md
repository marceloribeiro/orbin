# Distribution Guide for Orbin Package

This document explains how to prepare and distribute the Orbin package to PyPI so others can install it with `pip install orbin`.

## Prerequisites

Before you can distribute to PyPI, you need:

1. **PyPI Account**: Create accounts on both:
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Generate API tokens for uploading packages:
   - Go to your PyPI account settings
   - Create an API token for the entire account or specific project
   - Store these tokens securely

## Step-by-Step Distribution Process

### 1. Prepare Your Environment

```bash
# Install build tools
pip install build twine

# Optional: Install development dependencies
pip install -e .[dev]
```

### 2. Update Version Information

Before each release, update the version in:
- `pyproject.toml` (in the `[project]` section)
- `orbin/__init__.py` (the `__version__` variable)

```bash
# Example: updating to version 0.1.1
# Edit pyproject.toml: version = "0.1.1"
# Edit orbin/__init__.py: __version__ = "0.1.1"
```

### 3. Run Tests and Quality Checks

```bash
# Run tests
pytest

# Check code formatting
black --check orbin/

# Run type checking
mypy orbin/

# Check for linting issues
flake8 orbin/
```

### 4. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build
```

This creates:
- `dist/orbin-X.X.X-py3-none-any.whl` (wheel distribution)
- `dist/orbin-X.X.X.tar.gz` (source distribution)

### 5. Test Upload to Test PyPI

Always test your package on Test PyPI first:

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for username (use __token__) and password (your Test PyPI API token)
```

### 6. Test Installation from Test PyPI

```bash
# Create a new virtual environment for testing
python -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ orbin

# Test the installation
python -c "from orbin import hello_world; hello_world()"
```

### 7. Upload to Production PyPI

If testing is successful:

```bash
# Upload to production PyPI
python -m twine upload dist/*

# You'll be prompted for username (use __token__) and password (your PyPI API token)
```

### 8. Verify Installation

```bash
# Test installation from PyPI
pip install orbin

# Test functionality
python -c "from orbin import hello_world; hello_world()"
```

## Configuration Files for Automated Upload

### `.pypirc` Configuration

Create `~/.pypirc` to store repository configurations:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-api-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-api-token>
```

### Using twine with configuration

```bash
# Upload to Test PyPI using config
twine upload --repository testpypi dist/*

# Upload to PyPI using config
twine upload --repository pypi dist/*
```

## Automated Release with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Important Notes

### Version Management
- Always increment version numbers for new releases
- Follow [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH
- Never reuse version numbers

### Package Naming
- Package names on PyPI must be unique
- Check if "orbin" is available: `pip search orbin` or check PyPI directly
- Consider alternative names if "orbin" is taken

### File Exclusions
Create `.gitignore`:

```
# Build artifacts
build/
dist/
*.egg-info/

# Python cache
__pycache__/
*.pyc
*.pyo

# Virtual environments
venv/
env/

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
```

### Security Best Practices
- Never commit API tokens to version control
- Use environment variables or secure storage for tokens
- Regularly rotate API tokens
- Use 2FA on your PyPI account

## Troubleshooting

### Common Issues

1. **Package name already exists**: Choose a different name or namespace
2. **Upload fails**: Check your API token and internet connection
3. **Import errors**: Ensure `__init__.py` files are properly configured
4. **Version conflicts**: Make sure you're incrementing version numbers

### Verification Commands

```bash
# Check package metadata
python -m build --sdist --wheel
twine check dist/*

# Validate package structure
python setup.py check

# Test local installation
pip install -e .
python -c "import orbin; print(orbin.__version__)"
```

## Next Steps After Distribution

1. Monitor your package on PyPI for download statistics
2. Set up monitoring for issues and user feedback
3. Consider setting up continuous integration
4. Add more comprehensive documentation
5. Implement proper testing coverage
6. Add contribution guidelines

Remember to keep your package updated and respond to user issues promptly!
