# Copyright (c) 2020, DCSO GmbH

from collections import namedtuple
from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from . import temporal


class TestUTCNow(unittest.TestCase):
    def test_timezone_is_utc(self):
        now = temporal.utc_now()
        self.assertEqual(timezone.utc, now.tzinfo)


class TestDiffUTCNow(unittest.TestCase):
    @patch.object(temporal, 'utc_now')
    def test_stamp_after_now(self, mock_utc_now):
        now = datetime(2020, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        mock_utc_now.return_value = now

        diff = temporal.diff_utc_now(datetime(2020, 7, 15, 12, 0, 0, tzinfo=timezone.utc))
        self.assertGreater(diff.total_seconds(), 0)

    @patch.object(temporal, 'utc_now')
    def test_stamp_before_now(self, mock_utc_now):
        now = datetime(2020, 6, 14, 12, 0, 0, tzinfo=timezone.utc)
        mock_utc_now.return_value = now

        diff = temporal.diff_utc_now(datetime(2020, 5, 12, 0, 0, tzinfo=timezone.utc))
        self.assertLess(diff.total_seconds(), 0)


class TestDecodeUTCISO8601(unittest.TestCase):
    def test_valid(self):
        Case = namedtuple('Case', ['value', 'exp'])
        cases = [
            Case(value='2020-07-30T16:12:44.490868Z',
                 exp=datetime(2020, 7, 30, 16, 12, 44, 490868, tzinfo=timezone.utc)),
            Case(value='2020-07-30T16:12:44.490868 UTC',
                 exp=datetime(2020, 7, 30, 16, 12, 44, 490868, tzinfo=timezone.utc)),
            Case(value='2019-07-30T16:12:44.490868+00:00',
                 exp=datetime(2019, 7, 30, 16, 12, 44, 490868, tzinfo=timezone.utc)),
            Case(value='2019-10-31T12:35:49.350488666+00:00',
                 exp=datetime(2019, 10, 31, 12, 35, 49, 350489, tzinfo=timezone.utc)),
        ]

        for case in cases:
            with self.subTest(case=case, msg=case.value):
                self.assertEqual(case.exp, temporal.decode_utc_iso8601(case.value))

    def test_invalid(self):
        cases = [
            '2020-07-30T16:12:44.490868CEST',
            '2019-07-30T16:12:44.490868+02:00',
        ]

        for case in cases:
            with self.subTest(case=case):
                self.assertRaises(ValueError, temporal.decode_utc_iso8601, case)


if __name__ == '__main__':
    unittest.main()
