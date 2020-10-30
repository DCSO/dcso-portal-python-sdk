# Copyright (c) 2020, DCSO GmbH

import json
import unittest
from unittest.mock import patch, MagicMock

from ..exceptions import PortalAPIError
from dcso.glosom import Glosom, TYPE_ERROR, GROUP_SECURITY
from . import graphql


class TestGraphQLRequest(unittest.TestCase):
    @patch.object(graphql, 'urlopen')
    def test_pong(self, mock_urlopen):
        mm = MagicMock()
        mm.read.return_value = json.dumps({
            'data': {
                'ping': 'pong'
            }
        }).encode('utf-8')
        mock_urlopen.return_value = mm

        request = graphql.GraphQLRequest(query="{ ping }", api_url="http://127.0.0.1")
        res = request.execute_dict()

        self.assertEqual(res['data']['ping'], 'pong')

    @patch.object(graphql, 'urlopen')
    def test_with_error(self, mock_urlopen):
        mm = MagicMock()
        mm.read.return_value = json.dumps({
            'errors': [{
                'message': 'error occurred'
            }]
        }).encode('utf-8')
        mock_urlopen.return_value = mm

        request = graphql.GraphQLRequest(
            query="{ ping }", api_url="http://127.0.0.1",
        )

        with self.assertRaises(PortalAPIError) as ctx:
            request.execute_dict()

        self.assertEqual(str(ctx.exception), "error occurred")

    @patch.object(graphql, 'urlopen')
    def test_with_error(self, mock_urlopen):
        g = Glosom(gtype=TYPE_ERROR, group=GROUP_SECURITY,
                   message_id=0xB00D, service=0xAA,
                   message="not authorized")

        mm = MagicMock()
        mm.read.return_value = json.dumps(g.graphql_error()).encode('utf-8')
        mock_urlopen.return_value = mm

        request = graphql.GraphQLRequest(
            query="{ ping }", api_url="http://127.0.0.1"
        )

        with self.assertRaises(PortalAPIError) as ctx:
            request.execute_dict()

        self.assertEqual("not authorized (24B00DAA)", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
