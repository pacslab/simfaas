# version.py
# This code is used to tag docker builds for different versions of the
# library automatically.

import re
import os
import ast

# parse version from __init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_init_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "pacs-sls-sim", "__init__.py")
with open(_init_file, 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

print(version)
