exclude_patterns = ["_api/*"]

# docs/source/conf.py
import os, sys
sys.path.insert(0, os.path.abspath("../.."))

# Setting our titles and stuff
project = "mdsa-tools"
html_title = "mdsa-tools"
html_short_title = "mdsa-tools"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_design",
    "numpydoc",
    'sphinx_rtd_theme',
]

autosummary_generate = True

# Reduce duplication from numpydoc:
numpydoc_show_class_members = True
numpydoc_class_members_toctree = True

# So I can get attributes to work
napoleon_custom_sections = [
    ('Warnings', 'admonition'),
    ('Yield', 'params_style'),
    'API Notes'
]

# Reduces overhead
autodoc_mock_imports = [
    "mdtraj", "matplotlib", "seaborn", "sklearn", "umap", "pandas", "scipy",
    "pycircos"
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}



html_theme_options = {
    # Keep the logo/title at the left
    "navbar_start": ["navbar-logo"],

    # Keep search + theme switcher etc. on the right (optional)
    "navbar_end": ["search-field.html", "theme-switcher", "navbar-icon-links"],
    "show_nav_level": 2,
    "show_toc_level": 2,
}

# Theme settings (pydata_sphinx_theme)
html_theme = "ansys_sphinx_theme"
html_show_sourcelink = False

html_theme_options = {
    "logo": {
        "image_light": "images/stackerlogo.svg",
        "image_dark": "images/stacker_logo_dark.png",
    },
    "home_page_in_toc": True,
    "icon_links" : [
        {
            "name" : "PyPI",
            "url" : "https://pypi.org/project/pistacker/",
            "type": "url",
            "icon" : "https://raw.githubusercontent.com/esakkas24/stacker/refs/heads/main/docs/images/pypi.svg"
        }
    ],
    "navbar_start" : [],
    "navbar_center": ["navbar-nav"],
    "navbar_end": [
        "navbar-icon-links",
        "search-button-field"
    ],
    "header_links_before_dropdown": 4,
    "navbar_persistent": [],
    "github_url" : "https://github.com/esakkas24/stacker",
    "repository_url" : "https://github.com/esakkas24/stacker",
    "use_repository_button" : True,
    "collapse_navigation": True,
}



root_doc = "index"

# Static files (e.g., CSS) for customization
html_static_path = ["_static"]
html_css_files = ["fullwidth.css"]
