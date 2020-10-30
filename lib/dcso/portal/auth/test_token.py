# Copyright (c) 2020, DCSO GmbH

from copy import deepcopy
from datetime import datetime, timezone

from ..exceptions import PortalAPIResponse
from .token import Token
import unittest

_TEST_USER_TOKEN_10Y = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MTE3NjE4MzgsImlhdCI6MTU5NjQwMTgzOCwiaXNzIjoiZGNzbzphMyIsInN1YiI6IjVlZjI5OGU2LTg1ZGMtNGYzYS05ZGJlLTgxN2ZkYzAyMDlhMCIsImF1dGh6Ijp7Imdyb3VwcyI6WyJhMzpzdXBlciIsImEzOnVzZXIiXX0sImNudHIiOjYyNn0.szC8Sso6FqD_-83Z2K9_5_8L7n5t8WXUz6CO7BgsEmk'  # noqa
_TEST_USER_TOKEN_EXPIRED = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTYzODM5ODMsImlhdCI6MTU5NjM0Nzk4MywiaXNzIjoiZGNzbzphMyIsInN1YiI6IjVlZjI5OGU2LTg1ZGMtNGYzYS05ZGJlLTgxN2ZkYzAyMDlhMCIsImF1dGh6Ijp7Imdyb3VwcyI6WyJhMzpzdXBlciIsImEzOnVzZXIiXX0sImNudHIiOjUxM30.8VS5NjaJmjfLPqwKICUnxzOxW3EwBnWq_8jxv09siV4'  # noqa
_TEST_USER_TOKEN_TEMP = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE5MTE3NjI3OTUsImlhdCI6MTU5NjQwMjc5NSwiaXNzIjoiZGNzbzphMyIsInN1YiI6IjBkMDFhNDU2LTczYzEtMTFlOC05NGM3LTNkYmFlYzczNzgwMiIsImF1dGh6Ijp7Imdyb3VwcyI6W119LCJjbnRyIjo5OX0.w6V2Qyc5jGpqX9UVzW2O_Pt68cfWXJpdsaGmGx3JWm0'  # noqa
_TEST_USER_RESP = {'data': {'portalauth': {'user': {'id': '5ef298e6-85dc-4f3a-9dbe-817fdc0209a0', 'username': 'admin'},
                                           'token': _TEST_USER_TOKEN_10Y,
                                           'isTemporaryToken': False, 'otp': {'required': False, 'activated': None}}}}


class TestToken(unittest.TestCase):
    def test_init_graphql_response(self):
        auth = deepcopy(_TEST_USER_RESP)
        t = Token(graphql_response=auth['data']['portalauth'])
        self.assertEqual(_TEST_USER_TOKEN_10Y, t.token)

        exp = datetime(2030, 7, 31, 20, 57, 18, tzinfo=timezone.utc)
        self.assertEqual(exp, t.expires)
        self.assertFalse(t.is_expired())

    def test_init_graphql_response_expired_token(self):
        auth = deepcopy(_TEST_USER_RESP)
        auth['data']['portalauth']['token'] = _TEST_USER_TOKEN_EXPIRED
        try:
            t = Token(graphql_response=auth['data']['portalauth'])
        except PortalAPIResponse as exc:
            self.assertEqual("malformed user token (expired)", str(exc))

    def test_init_graphql_response_temporary(self):
        auth = deepcopy(_TEST_USER_RESP)
        auth['data']['portalauth']['token'] = _TEST_USER_TOKEN_TEMP
        t = Token(graphql_response=auth['data']['portalauth'])
        self.assertTrue(t.is_temporary)


if __name__ == '__main__':
    unittest.main()
