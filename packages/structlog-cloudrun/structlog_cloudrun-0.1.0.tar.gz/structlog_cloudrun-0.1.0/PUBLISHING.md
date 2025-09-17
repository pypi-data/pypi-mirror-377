# Publishing Guide

This document outlines the steps to publish the `structlog-cloudrun` package to PyPI using uv.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org/)
2. **API Token**: Generate a PyPI API token for this project
3. **uv**: Make sure uv is installed and up to date

## Pre-publishing Checklist

Before publishing, ensure:

- [ ] All tests pass: `uv run pytest`
- [ ] Code is properly formatted: `uvx ruff format`
- [ ] No linting issues: `uvx ruff check`
- [ ] Version number is updated in `pyproject.toml`
- [ ] README.md is up to date
- [ ] CHANGELOG or release notes are prepared
- [ ] All changes are committed to git

## Publishing Steps

### 1. Update Version

Use uv's built-in version management:

```bash
# For patch version (0.1.0 -> 0.1.1)
uv version --bump patch

# For minor version (0.1.0 -> 0.2.0)
uv version --bump minor

# For major version (0.1.0 -> 1.0.0)
uv version --bump major

# Or set specific version
uv version 1.0.0
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/

# Build source distribution and wheel
uv build
```

This creates:
- `dist/structlog_cloudrun-X.Y.Z.tar.gz` (source distribution)
- `dist/structlog_cloudrun-X.Y.Z-py3-none-any.whl` (wheel)

### 3. Test the Build

Verify the package can be installed:

```bash
# Test installation in isolated environment
uv run --with ./dist/structlog_cloudrun-*.whl --no-project -- python -c "import structlog_cloudrun; print('Import successful')"
```

### 4. Publish to PyPI

#### Method 1: Using PyPI Token (Recommended)

Set up your PyPI token as an environment variable:

```bash
export PYPI_TOKEN="pypi-your-token-here"
```

Then publish:

```bash
uv publish --token $PYPI_TOKEN
```

#### Method 2: Interactive Authentication

```bash
uv publish
# You'll be prompted for username and password
```

### 5. Verify Publication

After publishing:

1. Check the package page on PyPI: `https://pypi.org/project/structlog-cloudrun/`
2. Test installation from PyPI:

```bash
# In a new directory/environment
uv run --with structlog-cloudrun --no-project -- python -c "
import structlog_cloudrun
print(f'Successfully imported version: {structlog_cloudrun.__version__ if hasattr(structlog_cloudrun, \"__version__\") else \"unknown\"}')
"
```

## Test Publishing (TestPyPI)

Before publishing to the main PyPI, test with TestPyPI:

```bash
# Publish to TestPyPI
uv publish --repository testpypi --token $TESTPYPI_TOKEN

# Test installation from TestPyPI
uv run --with structlog-cloudrun --index-url https://test.pypi.org/simple/ --no-project -- python -c "import structlog_cloudrun"
```

## Troubleshooting

### Common Issues

1. **Version already exists**: Update the version number in `pyproject.toml`
2. **Authentication failed**: Check your API token or credentials
3. **Build fails**: Ensure all dependencies are properly specified
4. **Import errors**: Check package structure and `__init__.py` files

### Security Best Practices

- Use project-specific API tokens, not account-wide tokens
- Store tokens securely (environment variables, not in code)
- Consider using GitHub Actions for automated publishing
- Regularly rotate API tokens

## Automation with GitHub Actions

For automated publishing on tag creation, see the GitHub Actions workflow in `.github/workflows/publish.yml` (if created).

## Version Management Strategy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

## Post-Publication

After successful publication:

1. Create a git tag for the release
2. Update any documentation
3. Announce the release
4. Monitor for issues or feedback