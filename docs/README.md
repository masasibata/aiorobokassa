# Documentation

This directory contains the Sphinx documentation for aiorobokassa.

## Building Documentation

### Using Poetry

```bash
# Install documentation dependencies
poetry install --extras docs

# Build documentation
cd docs
poetry run sphinx-build -b html . _build/html

# Or use Makefile from project root
make docs
```

### Using Makefile

From the project root:

```bash
# Build documentation
make docs

# Build and serve locally
make docs-serve

# Clean build files
make docs-clean
```

## Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation page
- `installation.rst` - Installation guide
- `quickstart.rst` - Quick start guide
- `guides/` - Detailed guides
- `api/` - API reference
- `examples/` - Code examples
- `_static/` - Static files (CSS, images)
- `_templates/` - Custom templates

## Theme

Documentation uses the Furo theme for a modern, clean look.
