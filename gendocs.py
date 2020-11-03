#!/usr/bin/env python
# Copyright (c) 2020, DCSO GmbH

"""
We use pdoc3 to generate documentation. This script calls the runnable
script pdoc with fixed arguments. This is easier instead of using the pdoc-module.
"""

import os
import subprocess

_DOC_DIR = 'docs'
_HTML_DOC_DIR = os.path.join(_DOC_DIR)
_TEMPLATE_DIR = os.path.join('support', 'doc_templates')
_MODULES = ['lib/dcso']

if __name__ == '__main__':
    os.makedirs(_HTML_DOC_DIR, exist_ok=True)

    args = [
        'pdoc',
        '--html',
        '--force',
        '--template-dir', _TEMPLATE_DIR,
        '--output-dir', _HTML_DOC_DIR,
    ] + _MODULES

    subprocess.run(args)
