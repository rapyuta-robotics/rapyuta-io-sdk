# -*- coding: utf-8 -*-
import os
import sys

project = u'Rapyuta.io SDK'
copyright = u'2022, Rapyuta Robotics'
author = u'Rapyuta Robotics'

sys.path.insert(0, os.path.abspath('../..'))

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.autosummary',
              'sphinx.ext.ifconfig']

templates_path = ['_templates']
autosummary_generate = True  # Turn on sphinx.ext.autosummary
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = []
todo_include_todos = False

html_theme = "furo"
html_favicon = "favicon.ico"
html_static_path = ['_static']
html_theme_options = {
    "light_logo": "logo-light-mode.png",
    "dark_logo": "logo-dark-mode.png",
}
html_css_files = ['css/rio-sphinx.css']
html_js_files = ['js/rio-sphinx.js']
htmlhelp_basename = 'RIOdoc'
man_pages = [
    (master_doc, 'sdk', u'Rapyuta.io SDK',
     [author], 1)
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}
add_module_names = False
