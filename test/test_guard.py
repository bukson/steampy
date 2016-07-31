from unittest import TestCase

from steampy import guard


class TestGuard(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestGuard, self).__init__(*args, **kwargs)
        self.steam_guard_dict = guard.load_steam_guard('Steamguard')

    def test_one_time_code(self):
        shared_secret = self.steam_guard_dict['shared_secret']
        timestamp = 1469184207
        code = guard.generate_code_from_secret(shared_secret, timestamp)
        self.assertEquals(code, 'BJ3MJ')

    def test_confirmation_key(self):
        identity_secret = self.steam_guard_dict['identity_secret']
        timestamp = 1469372932
        confirmation_key = guard.generate_confirmation_key_from_secret(identity_secret, timestamp)
        self.assertEquals(confirmation_key, '')
