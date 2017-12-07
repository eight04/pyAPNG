#! python3

import re
import os.path
import sys

sys.path.insert(0, os.path.realpath(__file__ + "/../.."))
add_module_names = False
extensions = ["sphinx.ext.intersphinx", "sphinx.ext.autodoc"]
master_doc = "index"
autodoc_member_order = "bysource"
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
autoclass_content = 'both'
