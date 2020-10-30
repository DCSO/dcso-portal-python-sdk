# Copyright (c) 2020, DCSO GmbH

import os
import sys

from dcso.portal import APIClient, PortalAPIError, PortalAPIResponse, PortalException
from dcso.portal.auth import Authentication

# make sure we can read the common module
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from common import print_error, print_info  # nopep8 allowing import here

"""
Script which prompts for username and password, and authenticates with the DCSO Portal.
If 2FA is set up, it will also ask for TOTP code.
"""

try:
    if os.name == 'nt':
        import msvcrt

        def getch():
            return msvcrt.getch().decode()
    else:
        import tty
        import termios

        fd = sys.stdin.fileno()
        prev = termios.tcgetattr(fd)

        def getch():
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, prev)
            return ch

    def getpass(prompt):
        placeholder = '\N{MIDDLE DOT}'
        print(prompt, end='', flush=True)

        import curses

        pwd = bytearray()
        while True:
            c = getch()
            if ord(c) in (0x0a, 0x0d):
                print('')
                break
            elif ord(c) in (0x03, 0x04):  # Ctrl+C/Ctrl+D
                raise KeyboardInterrupt
            elif ord(c) in (0x08, 0x7F):  # backspace/delete
                pwd = pwd[:-1]
                clear = (len(prompt) + len(pwd) + 2) * ' '
                print(f"\r{clear}\r{prompt}{placeholder * len(pwd)}", end='', flush=True)
            else:
                pwd.append(ord(c))
                print(placeholder, end='', flush=True)
        return pwd.strip().decode(encoding='utf-8')

except ImportError:
    from getpass import getpass


def prompter(prompt, size=15, symbol: str = '') -> str:
    if symbol:
        size -= len(symbol)
    return f"{prompt:{size}} {symbol}: "


def prompt_input(prompt, echo: bool = True) -> str:
    if not echo:
        return getpass(prompt).strip()

    return input(prompt).strip()


def sign_on(client: APIClient, username: str, password: str) -> Authentication:
    try:
        auth = client.auth.authenticate(username=username, password=password)
    except (PortalAPIError, PortalAPIError, PortalAPIResponse):
        raise

    if auth.token.is_temporary:
        totp = prompt_input(prompter("TOTP", symbol='\N{KEY}'))
        auth = client.auth.second_authentication_totp(
            username=username,
            temp_token=auth.token.token,
            totp=totp)

    return auth


def main():
    try:
        if sys.argv[1]:
            url = sys.argv[1]
    except IndexError:
        print_error("first command line argument must be DCSO Portal API endpoint")
        sys.exit(1)

    client = APIClient(api_url=url)

    if not client.is_alive():
        print_error(f"failed using API {url}", exit=1)
    else:
        print_info(f"API {url} ready.")

    try:
        username = prompt_input(prompter("Username", symbol='\N{BUST IN SILHOUETTE}'))
        password = prompt_input(prompter("Password", symbol='\N{KEY}'), echo=False)
    except KeyboardInterrupt:
        print()
        print_info("Authentication cancelled")
        sys.exit(0)

    if not (username and password):
        print_error("need both username and password", exit=1)
        return

    try:
        auth = sign_on(client, username, password)
    except PortalException as exc:
        print_error(str(exc), exit=1)
    else:
        print(f"Your User Token expires {auth.token.expires}:\n{auth.token.token}")
        if auth.totp_activated:
            print("###", auth.totp_activated)
            print(f"TOTP Activated on: {auth.totp_activated.strftime('%c')}")
        client.token = auth.token.token

    try:
        perms = client.auth.user_service_permissions()
    except PortalException as exc:
        print_error(str(exc))
    else:
        print("\nYour Permissions")
        print("-------------------")
        for perm in iter(perms):
            print(f"{perm.service}: {perm.slug}")

        print(f"\nAccess as TDH Coordinator: {perms.have('tdh-access-admin')}")

    # graphql_execute returns named tuples
    response = client.execute_graphql(query='{ auth_user { id organization { shortCode } } }')
    print(f"Organization ShortCode: {response.auth_user.organization.shortCode}")


if __name__ == '__main__':
    main()
