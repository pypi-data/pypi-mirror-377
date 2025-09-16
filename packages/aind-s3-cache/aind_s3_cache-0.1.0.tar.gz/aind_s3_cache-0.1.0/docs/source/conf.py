"""Configuration file for the Sphinx documentation builder."""
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path Setup --------------------------------------------------------------
import sys
from datetime import date
from os.path import abspath, dirname
from pathlib import Path

# Add the project src directory to sys.path for imports
project_root = abspath(dirname(dirname(dirname(__file__))))
sys.path.insert(0, str(Path(project_root) / "src"))

from aind_s3_cache import __version__ as package_version  # noqa:E402

INSTITUTE_NAME = "Allen Institute for Neural Dynamics"

current_year = date.today().year

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "AIND S3 Cache"
copyright = f"{current_year}, {INSTITUTE_NAME}"
author = INSTITUTE_NAME
release = package_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "myst_nb",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "nbsphinx",
]
templates_path = ["_templates"]
exclude_patterns = []

# -- MyST-NB configuration --------------------------------------------------
# MyST-NB configuration for executable code blocks
nb_execution_mode = "cache"  # Use cache to avoid repeated execution
nb_execution_timeout = 30  # 30 second timeout per cell
nb_execution_cache_path = "docs/build/.jupyter_cache"  # Cache execution results
nb_execution_excludepatterns = []  # No exclusions by default
nb_execution_allow_errors = True  # Continue on errors for now

# MyST parser extensions
myst_enable_extensions = [
    "colon_fence",  # ::: code blocks
    "deflist",  # Definition lists
    "html_admonition",  # Callout boxes
    "substitution",  # Variable substitution
    "tasklist",  # Task lists
]

# -- Intersphinx configuration ----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "boto3": ("https://boto3.amazonaws.com/v1/documentation/api/latest/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

# -- Autodoc configuration --------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# -- Autosummary configuration ----------------------------------------------
autosummary_generate = True

# -- Napoleon configuration -------------------------------------------------
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/AllenNeuralDynamics/aind-s3-cache/",
    "source_branch": "main",
    "source_directory": "docs/source/",
}

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False
