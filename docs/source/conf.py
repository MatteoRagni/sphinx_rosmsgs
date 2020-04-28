import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../../..")))
from sphinx_rosmsgs.__version__ import __version__


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_fontawesome",
    "sphinx_rtd_theme"
]

project = 'Sphinx Extension for ROS Messages'
copyright = 'MIT License, 2020'
author = 'Matteo Ragni'
release = __version__

html_theme = "sphinx_rtd_theme"