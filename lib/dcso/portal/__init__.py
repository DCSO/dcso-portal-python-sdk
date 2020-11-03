# Copyright (c) 2020, DCSO GmbH

"""
.. include:: ./README.md

Usage
-----

### Initializing API Client

.. include:: ./apiclient.md

### Executing GraphQL Queries

DCSO Portal's API uses GraphQL. With the client object initialized, it is
possible to execute any GraphQL Query, which response is turned into
a namedtuple.

In the following example, we list all the DCSO TDH issues available to us:

    result = apic.execute_graphql(query='{ tdh_allIssues { id reference } }')
    for issue in result.tdh_allIssues:
        print(f"{issue.id} {issue.reference}")

Depending on the query, you will get sequence, or another nametuple. For example,
if you query a specific issue, using its UUID:

    issue_id = '3be13d5f-1556-4edf-a243-e7ea4db67f2e'
    query = '{ issue: tdh_issue(filter: {id: "'+issue_id+'"}) '+
        '{ title affectedAssets {ip} } }'

    result = apic.execute_graphql(query)

    print(result.issue.title)
    for asset in result.issue.affectedAssets:
        print(f"\t{asset.ip}")

Note that in the above example we also used an alias for (`{issue: tdh_issue..`}).
This make the following code more readable.

"""

__pdoc__ = {
    'test_api': False,
}

from .api import APIClient, ENV_PORTAL_TOKEN
from .exceptions import *
