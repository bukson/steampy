import unittest
from pathlib import Path
from unittest import TestCase

from steampy.client import SteamClient
from steampy.exceptions import TooManyRequests
from steampy.models import Currency, GameOptions
from steampy.utils import load_credentials


@unittest.skip('Requires secrets/Steamguard.txt')
class TestMarket(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.credentials = load_credentials()[0]
        dirname = Path(__file__).resolve().parent
        cls.steam_guard_file = f'{dirname}/../secrets/Steamguard.txt'

    def test_get_price(self) -> None:
        client = SteamClient(self.credentials.api_key)
        item = 'M4A1-S | Cyrex (Factory New)'
        prices = client.market.fetch_price(item, GameOptions.CS)
        assert prices['success']

    def test_get_price_to_many_requests(self) -> None:
        def request_loop() -> None:
            item = 'M4A1-S | Cyrex (Factory New)'
            for _ in range(21):
                client.market.fetch_price(item, GameOptions.CS)

        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        self.assertRaises(TooManyRequests, request_loop)

    def test_get_price_history(self) -> None:
        with SteamClient(
            self.credentials.api_key, self.credentials.login, self.credentials.password, self.steam_guard_file,
        ) as client:
            item = 'M4A1-S | Cyrex (Factory New)'
            response = client.market.fetch_price_history(item, GameOptions.CS)
            assert response['success']
            assert 'prices' in response

    def test_get_all_listings_from_market(self) -> None:
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        listings = client.market.get_my_market_listings()
        assert len(listings) == 2
        assert len(listings.get('buy_orders')) == 1
        assert len(listings.get('sell_listings')) == 1
        assert isinstance(next(iter(listings.get('sell_listings').values())).get('description'), dict)

    def test_create_and_remove_sell_listing(self) -> None:
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        game = GameOptions.DOTA2
        inventory = client.get_my_inventory(game)
        asset_id_to_sell = None
        for asset_id, item in inventory.items():
            if item.get('marketable') == 1:
                asset_id_to_sell = asset_id
                break
        assert asset_id_to_sell is not None, 'You need at least 1 marketable item to pass this test'
        response = client.market.create_sell_order(asset_id_to_sell, game, '10000')
        assert response['success']
        sell_listings = client.market.get_my_market_listings()['sell_listings']
        listing_to_cancel = None
        for listing in sell_listings.values():
            if listing['description']['id'] == asset_id_to_sell:
                listing_to_cancel = listing['listing_id']
                break
        assert listing_to_cancel is not None
        client.market.cancel_sell_order(listing_to_cancel)

    def test_create_and_cancel_buy_order(self) -> None:
        client = SteamClient(self.credentials.api_key)
        client.login(self.credentials.login, self.credentials.password, self.steam_guard_file)
        # PUT THE REAL CURRENCY OF YOUR STEAM WALLET, OTHER CURRENCIES WON'T WORK
        response = client.market.create_buy_order(
            'AK-47 | Redline (Field-Tested)', '10.34', 2, GameOptions.CS, Currency.EURO,
        )
        buy_order_id = response['buy_orderid']
        assert response['success'] == 1
        assert buy_order_id is not None
        response = client.market.cancel_buy_order(buy_order_id)
        assert response['success']
