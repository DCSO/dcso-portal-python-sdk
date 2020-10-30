# Copyright (c) 2020, DCSO GmbH

from copy import deepcopy
from datetime import datetime, timezone
import unittest

from .auth import Authentication
from .test_token import _TEST_USER_RESP


class TestAuth(unittest.TestCase):
    def test_something(self):
        auth = deepcopy(_TEST_USER_RESP)
        a = Authentication(graphql_response=auth['data']['portalauth'])

        exp = datetime(2030, 7, 31, 20, 57, 18, tzinfo=timezone.utc)
        self.assertEqual(exp, a.token.expires)
        self.assertFalse(a.token.is_expired())

        self.assertEqual(_TEST_USER_RESP['data']['portalauth']['user']['id'], a.id)
        self.assertEqual(_TEST_USER_RESP['data']['portalauth']['user']['username'], a.username)


if __name__ == '__main__':
    unittest.main()
