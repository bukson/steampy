from base64 import b64encode
from unittest import TestCase

from steampy import guard
from steampy.confirmation import Tag


class TestGuard(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shared_secret = b64encode(b'1234567890abcdefghij')
        cls.identity_secret = b64encode(b'abcdefghijklmnoprstu')

    def test_one_time_code(self) -> None:
        timestamp = 1469184207
        code = guard.generate_one_time_code(self.shared_secret, timestamp)
        assert code == 'P2QJN'

    def test_confirmation_key(self) -> None:
        timestamp = 1470838334
        confirmation_key = guard.generate_confirmation_key(self.identity_secret, Tag.CONF.value, timestamp)
        assert confirmation_key == b'pWqjnkcwqni+t/n+5xXaEa0SGeA='

    def test_generate_device_id(self) -> None:
        steam_id = '12341234123412345'
        device_id = guard.generate_device_id(steam_id)
        assert device_id == 'android:677cf5aa-3300-7807-d1e2-c408142742e2'

    def test_load_steam_guard(self) -> None:
        expected_keys = ('steamid', 'shared_secret', 'identity_secret')

        guard_json_str = '{"steamid": 12345678, "shared_secret": "SHARED_SECRET", "identity_secret": "IDENTITY_SECRET"}'
        guard_data = guard.load_steam_guard(guard_json_str)

        for key in expected_keys:
            assert key in guard_data
            assert isinstance(guard_data[key], str)
