import enum
from unittest import TestCase
from client import SteamClient, LoginRequired


def load_credentials():
    with open('credentials.pwd', 'r') as f:
        return [Credentials(line.split()[0], line.split()[1], line.split()[2]) for line in f]


class Credentials:
    def __init__(self, login: str, password: str, api_key: str):
        self.login = login
        self.password = password
        self.api_key = api_key


class TestSteamClient(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSteamClient, self).__init__(*args, **kwargs)
        self.credentials = load_credentials()[0]
        self.steam_guard_file = 'Steamguard'

    def test_get_trade_offers(self):
        client = SteamClient(self.credentials.api_key)
        result = client.get_trade_offers()
        self.assertEquals(result['status_code'], 200)

    def test_login(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        self.assertTrue(client.isLoggedIn)

    def test_accept_trade_offer_without_login(self):
        client = SteamClient(self.credentials.api_key)
        self.assertRaises(LoginRequired, client.accept_trade_offer, 'id')
