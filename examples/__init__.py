# Copyright (c) 2020, DCSO GmbH

import os
import sys

curr_wd = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, curr_wd)
print(sys.path)


def print_error(msg, exit: int = 0) -> None:
    print(f"Error \N{WARNING SIGN}️: {msg}")
    if exit > 0:
        sys.exit(exit)


def print_info(msg) -> None:
    print(msg)
