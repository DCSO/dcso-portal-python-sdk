# Copyright (c) 2020, DCSO GmbH

import sys

from dcso.portal import APIClient


def print_error(msg, exit: int = 0) -> None:
    print(f"Error \N{WARNING SIGN}️: {msg}")
    if exit > 0:
        sys.exit(exit)


def print_info(msg) -> None:
    print(msg)


def check_client(client: APIClient) -> None:
    if not client.is_alive():
        print_error(f"failed using API {client.api_url}", exit=1)
    else:
        print_info(f"API {client.api_url} ready.")
