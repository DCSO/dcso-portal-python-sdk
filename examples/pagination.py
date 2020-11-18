# Copyright (c) 2020, DCSO GmbH

"""
This script demonstrates:
* executes GraphQL query which support cursor-based pagination
* using machine tokens instead of credentials, reading the
  an environment variable (done automatically by SDK)

"""

import os
import sys
import time

from dcso.portal import APIClient, ENV_PORTAL_TOKEN, PortalConfiguration, PortalException


def main():
    url: str = ''
    try:
        if sys.argv[1]:
            url = sys.argv[1]
    except IndexError:
        print("first command line argument must be DCSO Portal API endpoint")
        sys.exit(1)

    try:
        # token will be set automatically later
        if os.environ[ENV_PORTAL_TOKEN] == "":
            raise KeyError
    except KeyError:
        print(f"please set environment variable {ENV_PORTAL_TOKEN} using valid DCSO Portal token")
        sys.exit(1)

    try:
        client = APIClient(api_url=url)
    except PortalConfiguration as exc:
        print(str(exc))
        sys.exit(1)

    q = """
query ($cursor: Cursor) { 
    alerts(first: 2 after: $cursor) {
        edges {
            node { id occurredOn }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

    variables = {
        'cursor': ''
    }

    have_more = True

    while have_more:
        try:
            response = client.execute_graphql(query=q, variables=variables)
        except PortalException as exc:
            print(str(exc))
            sys.exit(1)

        try:
            have_more = response.alerts.pageInfo.hasNextPage
            variables['cursor'] = response.alerts.pageInfo.endCursor
        except AttributeError as exc:
            print(exc)
            pass

        if len(response.alerts) > 0:
            for edge in response.alerts.edges:
                print(f"{edge.node.id} {edge.node.occurredOn}")
            if have_more:
                print(f".. more available with cursor {variables['cursor']}")
            time.sleep(2)

        if not have_more:
            print("No alerts available. Stopping.")
            break


if __name__ == '__main__':
    main()
