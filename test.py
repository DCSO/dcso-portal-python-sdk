#!/usr/bin/env python
# Copyright (c) 2020, DCSO GmbH

import os
import sys
import unittest

# we must update the PYTHONPATH, and for this we need the current working directory
curr_wd = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(curr_wd, 'lib'))


def suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    return loader.discover('./lib/dcso', pattern='test_*.py')


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
