import decimal
import os

from unittest import TestCase

from steampy.client import SteamClient
from steampy.exceptions import LoginRequired
from steampy.models import GameOptions, Asset
from steampy.utils import account_id_to_steam_id, load_credentials


class TestSteamClient(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials = load_credentials()[0]
        dirname = os.path.dirname(os.path.abspath(__file__))
        cls.steam_guard_file = dirname + '/../secrets/Steamguard.txt'

    def test_login(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)

    def test_is_session_alive(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        self.assertTrue(client.is_session_alive())

    def test_logout(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        self.assertTrue(client.is_session_alive())
        client.logout()

    def test_client_with_statement(self):
        with SteamClient(self.credentials.api_key, self.credentials.login,
                         self.credentials.password, self.steam_guard_file) as client:
            self.assertTrue(client.is_session_alive())

    def test_send_offer_without_sessionid_cookie(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        client._session.cookies.set('sessionid', None, domain="steamcommunity.com")
        cookies = client._session.cookies.get_dict('steamcommunity.com')
        self.assertFalse('sessionid' in cookies)
        game = GameOptions.TF2
        asset_id = ''
        my_asset = Asset(asset_id, game)
        trade_offer_url = ''
        make_offer = lambda: client.make_offer_with_url([my_asset], [], trade_offer_url, "TEST")
        self.assertRaises(AttributeError, make_offer)

    def test_sessionid_cookie(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        community_cookies = client._session.cookies.get_dict("steamcommunity.com")
        store_cookies = client._session.cookies.get_dict("store.steampowered.com")
        self.assertTrue("sessionid" in community_cookies)
        self.assertTrue("sessionid" in store_cookies)

    def test_get_my_inventory(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        inventory = client.get_my_inventory(GameOptions.CS)
        self.assertIsNotNone(inventory)

    def test_get_partner_inventory(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        partner_id = ''
        game = GameOptions.TF2
        inventory = client.get_partner_inventory(partner_id, game)
        self.assertIsNotNone(inventory)

    def test_get_trade_offers_summary(self):
        client = SteamClient(self.credentials.api_key)
        summary = client.get_trade_offers_summary()
        self.assertIsNotNone(summary)

    def test_get_trade_offers(self):
        client = SteamClient(self.credentials.api_key)
        offers = client.get_trade_offers()
        self.assertIsNotNone(offers)

    def test_get_trade_offer(self):
        client = SteamClient(self.credentials.api_key)
        trade_offer_id = '1442685162'
        offer = client.get_trade_offer(trade_offer_id)
        self.assertIsNotNone(offer)

    def test_accept_trade_offer_without_login(self):
        client = SteamClient(self.credentials.api_key)
        self.assertRaises(LoginRequired, client.accept_trade_offer, 'id')

    def test_accept_trade_offer(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        trade_offer_id = '1451378159'
        response_dict = client.accept_trade_offer(trade_offer_id)
        self.assertIsNotNone(response_dict)

    def test_decline_trade_offer(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        trade_offer_id = '1449530707'
        response_dict = client.decline_trade_offer(trade_offer_id)
        self.assertEqual(response_dict['response'], {})

    def test_cancel_trade_offer(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        trade_offer_id = '1450637835'
        response_dict = client.cancel_trade_offer(trade_offer_id)
        self.assertEqual(response_dict['response'], {})

    def test_make_offer(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        partner_id = ''
        game = GameOptions.CS
        my_items = client.get_my_inventory(game)
        partner_items = client.get_partner_inventory(partner_id, game)
        my_first_item = next(iter(my_items.values()))
        partner_first_item = next(iter(partner_items.values()))
        my_asset = Asset(my_first_item['id'], game)
        partner_asset = Asset(partner_first_item['id'], game)
        response = client.make_offer([my_asset], [partner_asset], partner_id, 'TESTOWA OFERTA')
        self.assertIsNotNone(response)
        self.assertIn('tradeofferid', response.keys())

    def test_make_offer_url(self):
        partner_account_id = '32384925'
        partner_token = '7vqRtBpC'
        sample_trade_url = 'https://steamcommunity.com/tradeoffer/new/?partner=' + partner_account_id + '&token=' + partner_token
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        client._session.request('HEAD', 'http://steamcommunity.com')
        partner_steam_id = account_id_to_steam_id(partner_account_id)
        game = GameOptions.CS
        my_items = client.get_my_inventory(game, merge=False)['rgInventory']
        partner_items = client.get_partner_inventory(partner_steam_id, game, merge=False)['rgInventory']
        my_first_item = next(iter(my_items.values()))
        partner_first_item = next(iter(partner_items.values()))
        my_asset = Asset(my_first_item['id'], game)
        partner_asset = Asset(partner_first_item['id'], game)
        response = client.make_offer_with_url([my_asset], [partner_asset], sample_trade_url, 'TESTOWA OFERTA')
        self.assertIsNotNone(response)
        self.assertIn('tradeofferid', response.keys())

    def test_get_escrow_duration(self):
        sample_trade_url = "https://steamcommunity.com/tradeoffer/new/?partner=314218906&token=sgA4FdNm"  # a sample trade url with escrow time of 15 days cause mobile auth not added
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        response = client.get_escrow_duration(sample_trade_url)
        self.assertEqual(response, 15)

    def test_get_wallet_balance(self):
        with SteamClient(self.credentials.api_key, self.credentials.login,
                         self.credentials.password, self.steam_guard_file) as client:
            wallet_balance = client.get_wallet_balance()
            self.assertTrue(type(wallet_balance), decimal.Decimal)
            wallet_balance = client.get_wallet_balance(convert_to_decimal=False)
            self.assertTrue(type(wallet_balance), str)
