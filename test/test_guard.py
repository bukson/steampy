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

    def test_generate_device_id(self):
        steam_id = "12341234123412345"
        device_id = guard.generate_device_id(steam_id)
        self.assertEquals(device_id, "android:677cf5aa-3300-7807-d1e2-c408142742e2")
