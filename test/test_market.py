import os

from unittest import TestCase

from steampy.client import SteamClient
from steampy.exceptions import TooManyRequests
from steampy.models import GameOptions, Currency
from steampy.utils import load_credentials


class TestMarket(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials = load_credentials()[0]
        dirname = os.path.dirname(os.path.abspath(__file__))
        cls.steam_guard_file = dirname + '/../secrets/Steamguard.txt'

    def test_get_price(self):
        client = SteamClient(self.credentials.api_key)
        item = 'M4A1-S | Cyrex (Factory New)'
        prices = client.market.fetch_price(item, GameOptions.CS)
        self.assertTrue(prices['success'])

    def test_get_price_to_many_requests(self):
        def request_loop() -> None:
            item = 'M4A1-S | Cyrex (Factory New)'
            for _ in range(21):
                client.market.fetch_price(item, GameOptions.CS)

        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        self.assertRaises(TooManyRequests, request_loop)

    def test_get_price_history(self):
        with SteamClient(self.credentials.api_key, self.credentials.login,
                         self.credentials.password, self.steam_guard_file) as client:
            item = 'M4A1-S | Cyrex (Factory New)'
            response = client.market.fetch_price_history(item, GameOptions.CS)
            self.assertTrue(response['success'])
            self.assertIn('prices', response)

    def test_get_all_listings_from_market(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        listings = client.market.get_my_market_listings()
        self.assertTrue(len(listings) == 2)
        self.assertTrue(len(listings.get("buy_orders")) == 1)
        self.assertTrue(len(listings.get("sell_listings")) == 1)
        self.assertIsInstance(next(iter(listings.get("sell_listings").values())).get("description"), dict)

    def test_create_and_remove_sell_listing(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        game = GameOptions.DOTA2
        inventory = client.get_my_inventory(game)
        asset_id_to_sell = None
        for asset_id, item in inventory.items():
            if item.get("marketable") == 1:
                asset_id_to_sell = asset_id
                break
        self.assertIsNotNone(asset_id_to_sell, "You need at least 1 marketable item to pass this test")
        response = client.market.create_sell_order(asset_id_to_sell, game, "10000")
        self.assertTrue(response["success"])
        sell_listings = client.market.get_my_market_listings()["sell_listings"]
        listing_to_cancel = None
        for listing in sell_listings.values():
            if listing["description"]["id"] == asset_id_to_sell:
                listing_to_cancel = listing["listing_id"]
                break
        self.assertIsNotNone(listing_to_cancel)
        response = client.market.cancel_sell_order(listing_to_cancel)

    def test_create_and_cancel_buy_order(self):
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        # PUT THE REAL CURRENCY OF YOUR STEAM WALLET, OTHER CURRENCIES WILL NOT WORK
        response = client.market.create_buy_order("AK-47 | Redline (Field-Tested)", "10.34", 2, GameOptions.CS,
                                                  Currency.EURO)
        buy_order_id = response["buy_orderid"]
        self.assertTrue(response["success"] == 1)
        self.assertIsNotNone(buy_order_id)
        response = client.market.cancel_buy_order(buy_order_id)
        self.assertTrue(response["success"])
