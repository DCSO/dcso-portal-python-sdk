# Copyright (c) 2020, DCSO GmbH

from collections import namedtuple
import unittest

from .glosom import *


class TestGlosom(unittest.TestCase):
    def test_init_decode(self):
        Case = namedtuple('Case', ['service', 'type', 'group', 'id'])
        cases = {
            0x131B0103: Case(service=0x03, type=0x01, group=0x03, id=0x1B01),
            0x2130ADB1: Case(service=0xB1, type=0x02, group=0x01, id=0x30AD),
        }

        for code, exp in cases.items():
            g = Glosom(code=code)
            self.assertEqual(g.service, exp.service)
            self.assertEqual(g.type, exp.type)
            self.assertEqual(g.group, exp.group)
            self.assertEqual(g.message_id, exp.id)

    def test_init_message(self):
        self.assertEqual(Glosom(message="not authorized").message, "not authorized")

    def test_init_encode(self):
        # without anything
        self.assertEqual(Glosom().code, 536870912)  # or 0x20000000

        # with service
        self.assertEqual(Glosom(service=0xAA).code, 536871082)  # or 0x200000aa

        self.assertEqual(Glosom(gtype=TYPE_ERROR, group=GROUP_SECURITY,
                                message_id=0xB00D, service=0xAA,
                                message="not authorized").code, 615517610)  # or 0x24B00Daa

    def test_init_code_str(self):
        self.assertEqual(Glosom(code='131B0103').code, 320536835)

        self.assertEqual(Glosom(code='spam').code, 0)

    def test_graphql_error(self):
        g = Glosom(gtype=TYPE_ERROR, group=GROUP_SECURITY,
                   message_id=0xB00D, service=0xAA,
                   message="not authorized")

        exp = {'errors': [{'extensions': {'code': 615517610}, 'message': 'not authorized'}]}
        self.assertDictEqual(g.graphql_error(), exp)


class TestGlosomException(unittest.TestCase):
    def test_raise_with_glosom(self):
        g = Glosom(gtype=TYPE_ERROR, group=GROUP_SECURITY,
                   message_id=0xB00D, service=0xAA,
                   message="not authorized")

        with self.assertRaises(GlosomException) as ctx:
            raise GlosomException(g)

        exp = "not authorized (24B00DAA)"
        self.assertEqual(str(ctx.exception), exp)

    def test_raise_with_glosom_without_code(self):
        g = Glosom()

        with self.assertRaises(GlosomException) as ctx:
            raise GlosomException(g)

        exp = "invalid message"
        self.assertEqual(str(ctx.exception), exp)


if __name__ == '__main__':
    unittest.main()
