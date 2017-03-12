import json

from requests import Session
from steampy.confirmation import ConfirmationExecutor
from steampy.exceptions import ApiException, TooManyRequests, LoginRequired
from steampy.models import Currency, SteamUrl, GameOptions
from steampy.utils import text_between, get_listing_id_to_assets_address_from_html, get_market_listings_from_html, \
    merge_items_with_descriptions_from_listing


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if not self.was_login_executed:
            raise LoginRequired('Use login method first on SteamClient')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


class SteamMarket:
    def __init__(self, session: Session):
        self._session = session
        self._steam_guard = None
        self._session_id = None
        self.was_login_executed = False

    def _login_executed(self, steamguard: dict, session_id: str):
        self._steam_guard = steamguard
        self._session_id = session_id
        self.was_login_executed = True

    def fetch_price(self, item_hash_name: str, game: GameOptions, currency: str = Currency.USD) -> dict:
        url = SteamUrl.COMMUNITY_URL + '/market/priceoverview/'
        params = {'country': 'PL',
                  'currency': currency,
                  'appid': game.app_id,
                  'market_hash_name': item_hash_name}
        response = self._session.get(url, params=params)
        if response.status_code == 429:
            raise TooManyRequests("You can fetch maximum 20 prices in 60s period")
        return response.json()

    @login_required
    def get_my_market_listings(self) -> dict:
        response = self._session.get("%s/market" % SteamUrl.COMMUNITY_URL)
        if response.status_code != 200:
            raise ApiException("There was a problem getting the listings. http code: %s" % response.status_code)
        assets_descriptions = json.loads(text_between(response.text, "var g_rgAssets = ", ";\r\n"))
        listing_id_to_assets_address = get_listing_id_to_assets_address_from_html(response.text)
        listings = get_market_listings_from_html(response.text)
        listings = merge_items_with_descriptions_from_listing(listings, listing_id_to_assets_address,
                                                              assets_descriptions)
        return listings

    @login_required
    def create_sell_listing(self, assetid: str, game: GameOptions, money_to_receive: int) -> dict:
        data = {
            "assetid": assetid,
            "sessionid": self._session_id,
            "contextid": game.context_id,
            "appid": game.app_id,
            "amount": 1,
            "price": money_to_receive
        }
        headers = {'Referer': "http://steamcommunity.com/profiles/%s/inventory" % self._steam_guard['steamid']}
        response = self._session.post("https://steamcommunity.com/market/sellitem/", data, headers=headers).json()
        if response.get("needs_mobile_confirmation"):
            return self._confirm_sell_listing(assetid)
        return response

    @login_required
    def create_buy_order(self, market_name: str, price_single_item: int, quantity: int, game: GameOptions,
                         currency: Currency = Currency.USD) -> dict:
        data = {
            "sessionid": self._session_id,
            "currency": currency.value,
            "appid": game.app_id,
            "market_hash_name": market_name,
            "price_total": price_single_item * quantity,
            "quantity": quantity
        }
        headers = {'Referer': "http://steamcommunity.com/market/listings/%s/%s" % (game.app_id, market_name)}
        response = self._session.post("https://steamcommunity.com/market/createbuyorder/", data,
                                      headers=headers).json()
        if response.get("success") != 1:
            raise ApiException("There was a problem creating the order. Are you using the right currency? success: %s"
                               % response.get("success"))
        return response

    @login_required
    def remove_sell_listing(self, sell_listing_id: str) -> None:
        data = {"sessionid": self._session_id}
        headers = {'Referer': "http://steamcommunity.com/market/"}
        url = "http://steamcommunity.com/market/removelisting/%s" % sell_listing_id
        response = self._session.post(url, data=data, headers=headers)
        if response.status_code != 200:
            raise ApiException("There was a problem removing the listing. http code: %s" % response.status_code)

    @login_required
    def cancel_buy_order(self, buy_order_id) -> dict:
        data = {
            "sessionid": self._session_id,
            "buy_orderid": buy_order_id
        }
        headers = {"Referer": "http://steamcommunity.com/market"}
        response = self._session.post("http://steamcommunity.com/market/cancelbuyorder/", data, headers=headers).json()
        if response.get("success") != 1:
            raise ApiException("There was a problem canceling the order. success: %s" % response.get("success"))
        return response

    def _confirm_sell_listing(self, asset_id: str) -> dict:
        con_executor = ConfirmationExecutor(self._steam_guard['identity_secret'], self._steam_guard['steamid'],
                                            self._session)
        return con_executor.confirm_sell_listing(asset_id)
