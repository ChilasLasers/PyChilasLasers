# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os,sys

sys.path.insert(0,os.path.abspath(".."))


project = 'PyChilasLasers'
copyright = '2025, Chilas B.V.'
author = 'Chilas B.V.'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.inheritance_diagram',
    'myst_parser',
    'sphinx_design',
    'sphinx_togglebutton',
    "sphinx_pyreverse"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_default_flags = ['members']
autosummary_generate = True

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}


# -- Options for autodoc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"

# Don't show class signature with the class' name.
autodoc_class_signature = "separated"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'private-members': False,
    'special-members': False,
    'inherited-members': False
}



import subprocess


def skip_member(app, what, name, obj, skip, options):
    # Skip private members
    if name.startswith('_'):
        return True
    # Skip inherited members
    if hasattr(obj, '__objclass__'):
        if obj.__objclass__.__name__ != options.get('objname', ''):
            return True
    return skip

def setup(app):
    app.connect("autodoc-skip-member", skip_member)





def safe_pyreverse():


    print()
    print()
    print()
    print("[sphinx_pyreverse] Generating UML diagrams with Pyreverse...")
    print(f"[sphinx_pyreverse] Current working directory: {os.getcwd()}")
    print()
    print()
    print()
  
  
    # Ensure pyreverse is installed and available in the environment
    try:
        subprocess.run(
            ['pyreverse', '--output', 'png', '-d' , './uml_images', "--no-standalone",  '../pychilaslasers'],
            check=False  # Don't raise CalledProcessError
        )
    except Exception as e:
        print(f"[sphinx_pyreverse] Pyreverse generation failed: {e}")

safe_pyreverse()