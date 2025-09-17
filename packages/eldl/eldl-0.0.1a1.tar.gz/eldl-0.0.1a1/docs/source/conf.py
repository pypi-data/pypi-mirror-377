from pathlib import Path
import sys

package = Path(__file__).parents[2].resolve().joinpath("src", "eldl")
sys.path.append(str(package))

# -- General Sphinx Options ------------------------------------------------------
extensions = [
    "notfound.extension",
    "sphinx.ext.apidoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.imgconverter",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_click",
    "sphinx_copybutton",
]
source_suffix = ".rst"
root_doc = "index"
project = "eldl"
version = release = "0.0.1a1"
author = "Ugochukwu Nwosu"
year = "2025"
copyright = f"{year}, {author}"
nitpicky = True
exclude_patterns = ["build"]
modindex_common_prefix = ["eldl."]
default_role = "code"
extlinks = {
    "issue": (
        "https://github.com/ugognw/eldl/issues/%s",
        "issue %s",
    ),
    "pr": (
        "https://github.com/ugognw/eldl/pulls/%s",
        "PR %s",
    ),
    "gitref": (
        "https://github.com/ugognw/eldl/commit/%s",
        "commit %s",
    ),
    "repo-file": (
        "https://github.com/ugognw/eldl/blob/main/%s",
        "`%s`",
    ),
}
linkcheck_ignore = [r"https://www.law-two.com"]
rst_epilog = r"""
.. |CO2RR| replace:: CO\ :sub:`2`\ RR
.. |H2| replace:: H\ :sub:`2`
.. |N2| replace:: N\ :sub:`2`
.. |H2O| replace:: H\ :sub:`2`\ O
.. |H2O2| replace:: H\ :sub:`2`\ O\ :sub:`2`
.. |NH3| replace:: NH\ :sub:`3`
.. |O2| replace:: O\ :sub:`2`
.. |NO2| replace:: NO\ :sub:`2`
.. |CH4| replace:: CH\ :sub:`4`
"""

# Options for LaTeX
latex_engine = "xelatex"

# -- Options for sphinx.ext.autodoc ------------------------------------------
autoclass_content = "both"



# -- Options for sphinx.ext.intersphinx --------------------------------------
intersphinx_mapping = {
    "ase": ("https://ase-lib.org/", None),
    "matplotlib": ("https://matplotlib.org/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pymatgen": ("https://pymatgen.org/", None),
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "click": ("https://click.palletsprojects.com/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "pydantic_settings": (
        "https://docs.pydantic.dev/",
        "_inventory/pydantic_settings/objects.inv",
    ),
    "FEniCSx": ("https://docs.fenicsproject.org/dolfinx/main/python/", None),
}

# -- Options for Napoleon ----------------------------------------------------
napoleon_google_docstring = True
napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_custom_sections = [("Keys", "Attributes")]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
# html_logo = "_static/eldl.png"
html_static_path = ["_static"]
html_last_updated_fmt = "%a, %d %b %Y %H:%M:%S"
html_theme_options = {
    "source_repository": "https://github.com/ugognw/eldl/",
    "source_branch": "main",
    "source_directory": "docs/source",
    "dark_css_variables": {
        "color-brand-primary": "#e0ffef",
        "color-brand-content": "#e0ffef",
    },
}
pygments_style = "sphinx"
pygments_dark_style = "monokai"

gitlab_url = "https://github.com/ugognw/eldl"

smartquotes = True
html_split_index = False
html_short_title = f"{project}-{version}"


# -- Options for sphinx_copybutton -------------------------------------------
copybutton_exclude = ".linenos, .gp, .go"
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
