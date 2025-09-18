exclude_patterns = ["_api/*"]

# docs/source/conf.py
import os, sys
sys.path.insert(0, os.path.abspath("../..")) 

project = "mdsa-tools"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]


#Since im using Numpy style docstrings the various preferences for things
napoleon_include_init_with_doc = False
autosummary_generate = True
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
autodoc_typehints = "description"
napoleon_include_special_with_doc = True
autoclass_content = "both"
napoleon_use_ivar = False
napoleon_attr_annotations = True

#so I can get attributes to work
napoleon_custom_sections = [
    ('Warnings', 'admonition'),          
    ('Yield', 'params_style'),           
    'API Notes', 'Attributes'                       
]

#reduces overhead
autodoc_mock_imports = [
    "mdtraj", "matplotlib", "seaborn", "sklearn", "umap", "pandas", "scipy",
    "pycircos"
]


autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

#this is theme specifications (see other file its in css so)
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
