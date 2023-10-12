# https://www.sphinx-doc.org/en/master/usage/configuration.html
# https://sphinx-rtd-theme.readthedocs.io/en/stable/index.html

project = 'xbutils'
copyright = ''
author = ''

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
]

autoclass_content = 'both'
add_module_names = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'

default_role = 'py:obj'