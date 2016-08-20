import base64
from unittest import TestCase

from steampy import guard
from steampy.confirmation import Tag


class TestGuard(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestGuard, self).__init__(*args, **kwargs)
        self.shared_secret = base64.b64encode('1234567890abcdefghij'.encode('utf-8'))
        self.identity_secret = base64.b64encode('abcdefghijklmnoprstu'.encode('utf-8'))

    def test_one_time_code(self):
        timestamp = 1469184207
        code = guard.generate_one_time_code(self.shared_secret, timestamp)
        self.assertEquals(code, 'P2QJN')

    def test_confirmation_key(self):
        timestamp = 1470838334
        confirmation_key = guard.generate_confirmation_key(self.identity_secret, Tag.CONF.value, timestamp)
        self.assertEquals(confirmation_key, b'pWqjnkcwqni+t/n+5xXaEa0SGeA=')
