"""Sphinx configuration file for aiorobokassa documentation."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Project information
project = "aiorobokassa"
copyright = "2025, Masa"
author = "Masa"
release = "1.0.2"
version = "1.0.2"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
]

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": "__init__",
}
autodoc_mock_imports = ["aiohttp", "pydantic"]
autosummary_generate = True

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# HTML theme
html_theme = "furo"
html_title = "aiorobokassa Documentation"
html_logo = "_static/logo.png"
html_theme_options = {
    "navigation_with_keys": True,
    "announcement": None,
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#0066CC",
        "color-brand-content": "#0066CC",
    },
    "dark_css_variables": {
        "color-brand-primary": "#4A9EFF",
        "color-brand-content": "#4A9EFF",
    },
}

# HTML static files
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Output options
html_show_sourcelink = True
html_show_sphinx = False

# Source files
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Language
language = "en"

