# Distribution Guide for Orbin Framework

This document explains how to prepare and distribute the Orbin framework to PyPI so developers can install it with `pip install orbin` and start building AI-powered chat applications.

## Prerequisites

Before you can distribute to PyPI, you need:

1. **PyPI Account**: Create accounts on both:
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Generate API tokens for uploading packages:
   - Go to your PyPI account settings
   - Create an API token for the entire account or specific project
   - Store these tokens securely

3. **Development Environment**:
   ```bash
   # Clone the repository
   git clone https://github.com/marceloribeiro/orbin.git
   cd orbin
   
   # Install in development mode
   pip install -e .
   ```

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

### 3. Pre-Release Quality Checks

Ensure the framework is ready for distribution:

```bash
# Run the test suite
python -m pytest tests/

# Test CLI functionality
orbin --help

# Test package imports
python -c "from orbin import hello_world; hello_world()"
python -c "from orbin.generators import AppGenerator; print('Generators OK')"
python -c "from orbin.cli import main; print('CLI OK')"

# Verify templates are included
python -c "from orbin.generators.base_generator import BaseGenerator; bg = BaseGenerator('test'); print(f'Templates dir: {bg.templates_dir}')"

# Check code quality (optional but recommended)
black --check orbin/
flake8 orbin/ --max-line-length=88 --extend-ignore=E203,E501
mypy orbin/ --ignore-missing-imports
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

Create a comprehensive test to ensure the framework works correctly:

```bash
# Create a clean test environment
python -m venv test_orbin_env
source test_orbin_env/bin/activate  # On Windows: test_orbin_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ orbin

# Test basic import
python -c "from orbin import hello_world; hello_world()"

# Test CLI is available
orbin --help

# Test framework functionality by creating a sample app
mkdir test_orbin_app
cd test_orbin_app
orbin create sample_app

# Verify the app structure was created
ls sample_app/
# Should show: app/, config/, db/, tests/, requirements.txt, etc.

# Test that generated app has proper dependencies
cd sample_app
pip install -r requirements.txt

# Clean up
cd ../../
rm -rf test_orbin_app
deactivate
rm -rf test_orbin_env
```

### 7. Upload to Production PyPI

If testing is successful:

```bash
# Upload to production PyPI
python -m twine upload dist/*

# You'll be prompted for username (use __token__) and password (your PyPI API token)
```

### 8. Verify Production Installation

Test the production installation thoroughly:

```bash
# Create a fresh environment
python -m venv prod_test_env
source prod_test_env/bin/activate

# Install from production PyPI
pip install orbin

# Test the complete workflow
mkdir orbin_production_test
cd orbin_production_test

# Test framework creation
orbin create test_chat_app
cd test_chat_app

# Verify structure
ls -la
# Should show complete Rails-like structure

# Test generators (without actually running them)
orbin generate --help

# Test CLI help
orbin --help

# Verify all components are working
python -c "
from orbin.generators.app_generator import AppGenerator
from orbin.generators.model_generator import ModelGenerator  
from orbin.generators.controller_generator import ControllerGenerator
from orbin.generators.resource_generator import ResourceGenerator
from orbin.generators.scaffold_generator import ScaffoldGenerator
from orbin.database import DatabaseManager
from orbin.cli import main
print('✅ All Orbin components imported successfully!')
"

# Clean up
cd ../../
rm -rf orbin_production_test
deactivate
rm -rf prod_test_env
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

Create `.github/workflows/publish.yml` for automated PyPI releases:

```yaml
name: Publish Orbin Framework to PyPI

on:
  release:
    types: [published]
  workflow_dispatch:  # Allow manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Test CLI functionality
      run: |
        orbin --help
        python -c "from orbin import hello_world; hello_world()"
        python -c "from orbin.generators import AppGenerator; print('OK')"

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    
    steps:
    - uses: actions/checkout@v4
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
    
    - name: Check package
      run: twine check dist/*
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### Setting up GitHub Secrets
1. Go to your repository → Settings → Secrets and variables → Actions
2. Add `PYPI_API_TOKEN` with your PyPI API token

## Important Notes

### Version Management
- Always increment version numbers for new releases
- Follow [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH
- Never reuse version numbers

## Important Framework-Specific Considerations

### Template Files Inclusion
Ensure Jinja2 templates are properly included in the distribution:

```toml
# In pyproject.toml - already configured
[tool.setuptools.package-data]
orbin = ["templates/**/*"]
```

```bash
# After building, check the wheel contents
python -m zipfile -l dist/orbin-*.whl | grep templates
# Should show all .j2 template files
```

Verify templates are included in the build:
```bash
# After building, check the wheel contents
python -m zipfile -l dist/orbin-*.whl | grep templates
# Should show all .j2 template files
```

### CLI Entry Point
The CLI should be accessible after installation:

```toml
# In pyproject.toml - already configured  
[project.scripts]
orbin = "orbin.cli:main"
```

Test the entry point:
```bash
# After installation
which orbin  # Should show the installed script
orbin --version  # Should show framework version
```

### Dependencies Management
Key dependencies for the framework:

```toml
# Core dependencies (in pyproject.toml)
dependencies = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0", 
    "sqlalchemy>=2.0.23",
    "alembic>=1.12.1",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
    "ipython>=8.0.0",
    "jinja2>=3.0.0",
    "inflect>=7.0.0",
]
```

### Package Naming and Availability
- "orbin" appears to be available on PyPI (as of August 2025)
- If taken, consider alternatives: `orbin-framework`, `orbin-rails`, `orbin-ai`
- Check availability: https://pypi.org/project/orbin/

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

### Framework-Specific Validation

```bash
# Validate framework completeness
python -m build --sdist --wheel
twine check dist/*

# Test package structure
python -c "
import zipfile
import sys
with zipfile.ZipFile(sys.argv[1], 'r') as z:
    files = z.namelist()
    templates = [f for f in files if 'templates/' in f]
    print(f'Templates found: {len(templates)}')
    if len(templates) == 0:
        print('ERROR: No templates found!')
        sys.exit(1)
    print('✅ Templates included correctly')
" dist/orbin-*.whl

# Test CLI entry point
pip install dist/orbin-*.whl
orbin --version
orbin --help

# Test import structure
python -c "
try:
    from orbin.generators.app_generator import AppGenerator
    from orbin.generators.model_generator import ModelGenerator
    from orbin.generators.controller_generator import ControllerGenerator
    from orbin.generators.resource_generator import ResourceGenerator
    from orbin.generators.scaffold_generator import ScaffoldGenerator
    from orbin.database import DatabaseManager
    from orbin.cli import main
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
```

## Post-Distribution Framework Maintenance

After successfully publishing Orbin to PyPI:

### 1. Monitor Framework Adoption
- Track download statistics on PyPI
- Monitor GitHub issues and discussions
- Set up alerts for critical issues

### 2. Community Engagement
- Respond to user questions and bug reports
- Create examples and tutorials
- Maintain comprehensive documentation
- Consider creating a Discord/Slack community

### 3. Framework Evolution
- Regularly update dependencies (FastAPI, SQLAlchemy, etc.)
- Add new generator types based on user feedback
- Implement additional Rails patterns
- Enhance AI/chat specific features

### 4. Quality Assurance
- Set up comprehensive CI/CD pipelines
- Implement integration tests with real databases
- Test compatibility with different Python versions
- Validate against multiple operating systems

### 5. Documentation and Examples
- Create a documentation website (consider GitHub Pages)
- Build example AI chat applications
- Write tutorials for common use cases
- Document best practices for AI/agent development

### 6. Versioning Strategy
Follow semantic versioning for framework releases:
- **Patch** (0.1.x): Bug fixes, small improvements
- **Minor** (0.x.0): New features, additional generators
- **Major** (x.0.0): Breaking changes, major architectural updates

### 7. Backward Compatibility
- Maintain backward compatibility within major versions
- Provide migration guides for breaking changes
- Deprecate features gradually with clear timelines

Remember: As a framework, Orbin's success depends on developer adoption and community feedback. Prioritize stability, clear documentation, and responsive support!
