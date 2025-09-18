exclude_patterns = ["_api/*"]

# docs/source/conf.py
import os, sys
sys.path.insert(0, os.path.abspath("../..")) 

#Setting our titles and stuff
project = "mdsa-tools"
html_title = "mdsa-tools"        
html_short_title = "mdsa-tools"


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_design",
    "numpydoc",
]

autosummary_generate = True


# Reduce duplication from numpydoc:
numpydoc_show_class_members = True
numpydoc_class_members_toctree = True


#so I can get attributes to work
napoleon_custom_sections = [
    ('Warnings', 'admonition'),          
    ('Yield', 'params_style'),           
    'API Notes'                     
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
html_theme = "pydata_sphinx_theme"
html_show_sourcelink = False

#html_static_path = ['../_static']
#html_css_files = ['custom.css']