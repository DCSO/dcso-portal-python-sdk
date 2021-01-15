# Copyright (c) 2020, 2021, DCSO GmbH

import os
import sys

from setuptools import setup, find_namespace_packages

# we must update the PYTHONPATH, and for this we need the current working directory
curr_wd = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(curr_wd, 'lib'))

from lib.dcso.portal._version import __version__  # nopep8 allowing import here

with open(os.path.join(os.path.abspath(curr_wd), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='dcso_portal_python_sdk',
      version=__version__,
      description="DCSO Portal SDK",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='DCSO GmbH',
      author_email='portal-support@dcso.de',
      url="https://dcso.github.io/dcso-portal-python-sdk/dcso/portal/",
      package_dir={'': 'lib'},
      packages=find_namespace_packages(where='lib'),
      license='MIT License',
      license_files=['LICENSE.txt'],
      platforms=['Any'],
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.7",
          "Operating System :: OS Independent",
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Topic :: Software Development",
          "Topic :: Software Development :: Version Control :: Git",
      ],
      )
