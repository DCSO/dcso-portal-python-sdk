# Copyright (c) 2020, DCSO GmbH

import json
import ssl
from collections import namedtuple
from datetime import datetime, timezone
from os import environ
from typing import AnyStr, List, Optional, Union
from urllib.error import URLError
from urllib.parse import ParseResult, urlparse
from urllib.request import Request, urlopen

from dcso.glosom import Glosom
from ..exceptions import PortalAPIError, PortalAPIRequest
from ..util.temporal import decode_utc_iso8601

_ENV_SKIP_TLS_VERIFY = "DCSO_PORTAL_SKIP_TLS_VERIFY"


class GraphQLJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.replace(tzinfo=timezone.utc).isoformat()

        return super().default(o)


class GraphQLJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        try:
            del kwargs['object_hook']
        except KeyError:
            # ok when not in kwargs
            pass
        super().__init__(*args, **kwargs, object_hook=self.object_hook)

    @staticmethod
    def object_hook(o: dict) -> dict:
        for k, v in o.items():
            try:
                o[k] = decode_utc_iso8601(v)
            except ValueError as exc:
                # not an ISO date formatted string; let others figure it out
                pass

        return o


class GraphQLRequest:
    def __init__(self,
                 query: str,
                 api_url: Union[ParseResult, str],
                 variables: Optional[dict] = None,
                 fragments: Optional[List[str]] = None,
                 token: Optional[str] = None):
        self.query: str = query
        self.api_url: Union[ParseResult, str] = api_url
        self.variables: dict = variables
        self.fragments: List[str] = fragments
        self.token: Optional[str] = token

    def json(self) -> bytes:
        q = self.query
        if self.fragments:
            q += '\n'.join(self.fragments)

        r = {
            'query': q
        }

        if self.variables:
            r['variables'] = self.variables

        return json.dumps(r, cls=GraphQLJSONEncoder).encode('utf-8')

    def execute_raw(self) -> AnyStr:
        """Executes the GraphQL query and return the response from the wire as JSON.

        This method is not to be used directly unless JSON must be process different.
        Methods `execute_dict` and `execute` have a more Pythonic result, and easier
        to use.

        Raises PortalAPIRequest when request with API or decoding result fails.
        """
        headers = {
            'Content-Type': 'application/json'
        }

        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token

        url = self.api_url
        if isinstance(url, str):
            url = urlparse(self.api_url)

        req = Request(url.geturl(), headers=headers, method='POST', data=self.json())

        ssl_ctx = None
        if url.scheme == 'https':
            ssl_ctx = ssl.SSLContext()
            if environ.get(_ENV_SKIP_TLS_VERIFY):
                ssl_ctx.verify_mode = ssl.CERT_NONE

        try:
            return urlopen(req, context=ssl_ctx).read()
        except URLError as exc:
            raise PortalAPIRequest(str(exc.reason))

    def execute_dict(self) -> dict:
        """Executes the GraphQL request returning response as a dictionary.

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        res = self.execute_raw()
        if isinstance(res, bytes):
            res = res.decode('utf-8')

        try:
            response = json.loads(res, cls=GraphQLJSONDecoder)
        except json.JSONDecodeError as exc:
            raise PortalAPIRequest("failed decoding API response: " + str(exc))

        try:
            first_error = response['errors'][0]
        except (TypeError, KeyError, IndexError):
            # all is good; return response
            return response

        try:
            err = first_error['message']
            code = ""
            if 'extensions' in first_error:
                if 'detail' in first_error['extensions']:
                    err += ' (' + first_error['extensions']['detail'] + ')'
                code = first_error['extensions'].get('code', "")
            g = Glosom(message=first_error['message'], code=code)
        except KeyError as exc:
            raise PortalAPIRequest(f"API request contained unusable error definition {exc}")
        except AttributeError:
            raise PortalAPIRequest(f"API request contained unusable error extensions")
        else:
            raise PortalAPIError(glosom=g)

    def execute(self) -> namedtuple:
        """Executes the GraphQL request returning response as a namedtuple.

        This method wraps around the `execute` method, but returns instead of
        dict, a namedtuple which itself might contain namedtuples.

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        return graphql_data_to_namedtuple(self.execute_dict()['data'])


def graphql_data_to_namedtuple(mapping: dict, name: str = 'data') -> namedtuple:
    """Transforms GraphQL response data and returns it as a namedtuple.

    This method takes the mapping as GraphQL Response data and recursively goes
    through it converting dict object to namedtuple, and array of objects as list.

    The name of the namedtuple is the key of value it is created from. The
    starting named tuple is by default called 'data'.
    """
    if isinstance(mapping, dict):
        for key, value in mapping.items():
            if isinstance(value, (list, tuple)):
                for idx, p in enumerate(value):
                    value[idx] = graphql_data_to_namedtuple(p, key)
            else:
                mapping[key] = graphql_data_to_namedtuple(value, key)
        return namedtuple(name, field_names=mapping.keys())(*mapping.values())
    return mapping
