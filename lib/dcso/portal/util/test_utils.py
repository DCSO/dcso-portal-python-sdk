# Copyright (c) 2020, DCSO GmbH

import unittest

from ..exceptions import PortalConfiguration
from .networking import validate_api_url, _API_URI_MAX_LEN


class TestValidateAPIURL(unittest.TestCase):
    def test_valid(self):
        cases = [
            'http://localhost:8080/graphql',
            'https://api.example.com/apis/graphql',
            'http://example.com/with/padding    '
        ]

        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(validate_api_url(case), case.strip())

    def test_invalid(self):
        cases = [
            'ftp://localhost/graphql',
            'http:///no/domain',
            'https://example.com/?sql=spam',
            'https://example.com/graphql#spam'
            'http://waytolongthisurlis.io' + 'a'*_API_URI_MAX_LEN
        ]

        for case in cases:
            with self.subTest(case=case):
                self.assertRaises(PortalConfiguration, validate_api_url, case)


if __name__ == '__main__':
    unittest.main()
