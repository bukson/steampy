import enum
import requests
from steampy import guard
from steampy.confirmation import ConfirmationExecutor
from steampy.login import LoginExecutor


class Currency(enum.Enum):
    USD = '1'
    GBP = '2'
    EURO = '3'
    CHF = '4'


class GameOptions(enum.Enum):
    DOTA2 = ('570', '2')
    CS = ('730', '2')

    def __init__(self, app_id: str, context_id: str) -> None:
        self.app_id = app_id
        self.context_id = context_id


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if not self.isLoggedIn:
            raise LoginRequired('Use login method first')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


class LoginRequired(Exception):
    pass


class SteamClient:
    API_URL = "https://api.steampowered.com"
    BASE_URL = "https://steamcommunity.com"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._session = requests.Session()
        self.steam_guard = None
        self.isLoggedIn = False

    def login(self, username: str, password: str, steam_guard: str) -> None:
        self.steam_guard = guard.load_steam_guard(steam_guard)
        LoginExecutor(username, password, self.steam_guard['shared_secret'], self._session).login()
        self.isLoggedIn = True

    def get_my_inventory(self, game: GameOptions) -> dict:
        url = self.BASE_URL + '/my/inventory/json/' + \
              game.app_id + '/' + \
              game.contex_id
        return self._session.get(url).json()

    def api_call(self, request_method: str, interface: str, api_method: str, version: str,
                 params: dict = None) -> requests.Response:
        url = '/'.join([self.API_URL, interface, api_method, version])
        return requests.request(request_method, url, data=params)

    def get_trade_offers_summary(self) -> dict:
        return self.api_call('GET', 'ISteamWebAPIUtil', 'GetTradeOffersSummary', 'v1').json()

    def get_trade_offers(self) -> dict:
        params = {'key': self._api_key,
                  'get_sent_offers': 0,
                  'get_received_offers': 1,
                  'get_descriptions': 1,
                  'language': 'english',
                  'active_only': 1,
                  'historical_only': 0,
                  'time_historical_cutoff': ''}
        return self.api_call('GET', 'IEconService', 'GetTradeOffers', 'v1', params).json()

    def get_trade_offer(self, trade_offer_id: str) -> dict:
        params = {'key': self._api_key,
                  'tradeofferid': trade_offer_id,
                  'language': 'english'}
        return self.api_call('GET', 'IEconService', 'GetTradeOffer', 'v1', params).json()

    @login_required
    def accept_trade_offer(self, trade_offer_id: str) -> dict:
        accept_url = self.BASE_URL + '/tradeoffer/' + trade_offer_id + '/accept'  # body ważne?
        self._session.post(accept_url)
        return ConfirmationExecutor(trade_offer_id, self.steam_guard['identity_secret'],
                                    self.steam_guard['steamid'], self._session).send_trade_allow_request()

    def decline_trade_offer(self, trade_offer_id: str) -> dict:
        params = {'key': self._api_key,
                  'tradeofferid': trade_offer_id}
        return self.api_call('POST', 'IEconService', 'DeclineTradeOffer', 'v1', params).json()

    def cancel_trade_offer(self, trade_offer_id: str) -> dict:
        params = {'key': self._api_key,
                  'tradeofferid': trade_offer_id}
        return self.api_call('POST', 'IEconService', 'CancelTradeOffer', 'v1', params).json()

    def get_price(self, item_hash_name: str, game: GameOptions, currency: str = Currency.USD) -> dict:
        url = self.BASE_URL + '/market/priceoverview/'
        params = {'country': 'PL',
                  'currency': currency,
                  'appid': game.app_id,
                  'market_hash_name': item_hash_name}
        return self._session.get(url, params=params).json()
