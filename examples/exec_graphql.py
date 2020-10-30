# Copyright (c) 2020, DCSO GmbH

"""
This script demonstrates:
* using machine tokens instead of credentials, reading the
  an environment variable (done automatically by SDK)
* executes GraphQL queries and uses the namedtuple to display result
"""

import os
import sys

from dcso.portal import APIClient, PortalConfiguration, ENV_PORTAL_TOKEN

# make sure we can read the common module
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from common import print_error, check_client  # nopep8 allowing import here


def main():
    url: str = ''
    try:
        if sys.argv[1]:
            url = sys.argv[1]
    except IndexError:
        print_error("first command line argument must be DCSO Portal API endpoint")
        sys.exit(1)

    try:
        # token will be set automatically later
        if os.environ[ENV_PORTAL_TOKEN] == "":
            raise KeyError
    except KeyError:
        print_error(f"please set environment variable {ENV_PORTAL_TOKEN} using valid DCSO Portal token")
        sys.exit(1)

    try:
        client = APIClient(api_url=url)
    except PortalConfiguration as exc:
        print_error(str(exc))
        sys.exit(1)

    check_client(client)

    response = client.execute_graphql(query='{ tdh_allIssues { id reference } }')
    print("All TDH Issues:")
    for issue in response.tdh_allIssues:
        print(f"{issue.id} {issue.reference}")

    issue_id = '3be13d5f-1556-4edf-a243-e7ea4db67f2e'
    query = """query {
issue: tdh_issue(filter: {id: "%s"}) {
        title
        affectedAssets {ip}
    }
}""" % (issue_id,)

    result = client.execute_graphql(query)
    print(f"\n{result.issue.title} ({issue_id})")
    for asset in result.issue.affectedAssets:
        print(f"Assets:\n\t{asset.ip}")


if __name__ == '__main__':
    main()
