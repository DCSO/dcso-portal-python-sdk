# Copyright (c) 2020, DCSO GmbH

from copy import deepcopy
from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from . import api
from .exceptions import PortalConfiguration

_TEST_API_URI = 'http://127.0.0.1:9170'


class TestAPIClient(unittest.TestCase):
    def test_init_api_url(self):
        with self.subTest("valid"):
            exp = "http://example.com/graphql"
            self.assertEqual(api.APIClient(exp).api_url, exp)

        with self.subTest("invalid"):
            exp = "ftp://example.com/graphql"
            self.assertRaises(PortalConfiguration, api.APIClient, api_url=exp)

    @patch.object(api.GraphQLRequest, 'execute_dict')
    def test_graphql_execute(self, mock_execute_dict):
        graphql_response = {
            'data': {
                'fields': {
                    'fieldNumber': 1234,
                    'fieldString': 'string',
                    'fieldDate': datetime(2016, 4, 2, 23, 1, 2, tzinfo=timezone.utc),
                    'nested': {
                        'fieldA': 'This if field A',
                        'fieldP': 3.14,
                    },
                    'array': [
                        {
                            'id': 1,
                            'ham': 'first entry',
                        },
                        {
                            'id': 2,
                            'ham': 'second entry',
                        }
                    ],
                    'arrayOfNonDicts': ['ham', 'spam']
                }
            }
        }
        mock_execute_dict.return_value = deepcopy(graphql_response)

        gql = api.APIClient(api_url=_TEST_API_URI)
        resp = gql.execute_graphql(query="{ does { not { matter } } }")
        fields = resp.fields

        exp = graphql_response['data']['fields']
        self.assertEqual(exp['fieldNumber'], fields.fieldNumber)
        self.assertEqual(exp['fieldString'], fields.fieldString)
        self.assertEqual(exp['fieldDate'], fields.fieldDate)
        self.assertEqual(exp['nested']['fieldA'], fields.nested.fieldA)
        self.assertEqual(exp['nested']['fieldP'], fields.nested.fieldP)

        for idx, exp_item in enumerate(exp['array']):
            self.assertEqual(exp_item['id'], fields.array[idx].id)

        self.assertEqual(exp['arrayOfNonDicts'], fields.arrayOfNonDicts)


if __name__ == '__main__':
    unittest.main()
