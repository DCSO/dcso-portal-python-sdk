# Copyright (c) 2020, DCSO GmbH

"""
Definition of the APIClient class which is used to start interactions with
the DCSO Portal API.
"""
import os
import urllib.parse
from collections import namedtuple
from typing import List, Optional

from .abstracts import APIAbstract
from .auth import Auth
from .exceptions import PortalAPIRequest, PortalException
from .util.graphql import GraphQLRequest
from .util.networking import validate_api_url

ENV_PORTAL_TOKEN: str = "DCSO_PORTAL_TOKEN"
"""Name of the environment variable holding the
DCSO Portal Token to be used when Authorizing."""


class APIClient(APIAbstract):
    """
    .. include:: apiclient.md
    """

    def __init__(self, api_url: str):
        """
        The `api_url` parameter is the DCSO Portal API endpoint and must be provided;
        there is no default.
        """
        self._api_url: str = ""
        self.api_url = api_url
        self._token: str = os.environ.get(ENV_PORTAL_TOKEN, "")

        # default services
        self.auth = Auth(api=self)

    @property
    def api_url(self) -> str:
        return self._api_url

    @api_url.setter
    def api_url(self, url: str) -> None:
        """Sets the API endpoint using the provided url. Raises `DCSOPortalConfiguration`
        when url is not valid.
        """
        self._api_url = validate_api_url(url)

    def api_url_parsed(self) -> urllib.parse.ParseResult:
        return urllib.parse.urlparse(self._api_url)

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, token: str):
        """Sets the token for each API request. This can be either a User Token (JWT)
        or a Machine Token (also known as API Token).
        """
        self._token = token

    def execute_graphql(self, query: str,
                        variables: Optional[dict] = None,
                        fragments: Optional[List[str]] = None) -> namedtuple:
        """Executes the GraphQL query and returns response as namedtuple. This
        namedtuple starts from the 'data'-object.

        For example, when executing query getting user information:

            response = execute_graphql(`{ user { id name }`)

        the resulting GraphQL JSON might look as follows:

            {
                "data": {
                    "user": { "id": "1234", "name": "Alice" }
                }
            }

        Then retrieving and print the name of the user using the response:

            print(f"Name: {response.user.name}")

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        request = GraphQLRequest(api_url=self.api_url,
                                 query=query, variables=variables, fragments=fragments,
                                 token=self.token)

        try:
            return request.execute()
        except PortalException:
            raise

    def execute_graphql_dict(self, query: str,
                             variables: Optional[dict] = None,
                             fragments: Optional[List[str]] = None) -> dict:
        """Executes the GraphQL request and return response a dictionary.

        For example, when executing query getting user information:

            response = execute_graphql_dict(`{ user { id name }`)

        the resulting GraphQL JSON might look as follows:

            {
                "data": {
                    "user": { "id": "1234", "name": "Alice" }
                }
            }

        Then retrieving and print the name of the user using the response:

            print(f"Name: {response['user']['name']}")

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        request = GraphQLRequest(api_url=self.api_url,
                                 query=query, variables=variables, fragments=fragments,
                                 token=self.token)

        try:
            return request.execute_dict()['data']
        except KeyError as exc:
            raise PortalAPIRequest(f"API request contained unusable error definition {exc}")
        except PortalException:
            raise

    def is_alive(self) -> bool:
        """Returns whether it is possible to communicate with API endpoint."""
        request = GraphQLRequest(
            api_url=self.api_url,
            query='{__schema { queryType { name }}}'
        )

        try:
            result = request.execute_dict()
            return 'Query' == result['data']['__schema']['queryType']['name']
        except (KeyError, PortalException):
            return False
