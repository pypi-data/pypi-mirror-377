# wingman-run

Real-time typo fixer that streams corrections from an LLM into your focused text area.

## Development Setup

### Prerequisites

- Python 3.10+
- pip
- macOS (for now, uses macOS-specific accessibility APIs)

### Install for Development

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install package in editable mode with dependencies
pip install -e .

# Test the CLI
wingman-run
```

## Deployment

### Build Distribution Packages

```bash
# Install build tools
pip install build

# Build wheel and source distributions
python -m build

# This creates:
# - dist/wingman_run-0.1.0-py3-none-any.whl
# - dist/wingman_run-0.1.0.tar.gz
```

### Test with TestPyPI (Recommended First Step)

```bash
# Install twine for uploading
pip install twine

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ wingman-run
```

### Publish to PyPI

```bash
# Upload to PyPI (requires account and API token)
twine upload dist/*

# Users can then install with:
# pip install wingman-run
```

### PyPI Account Setup

1. Create account at [pypi.org](https://pypi.org)
2. Generate API token in Account Settings
3. When uploading, use:
   - Username: `__token__`
   - Password: Your API token