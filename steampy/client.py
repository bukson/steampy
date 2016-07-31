import enum
import requests
from steampy import guard
from steampy.confirmation import ConfirmationExecutor
from steampy.login import LoginExecutor, InvalidCredentials
from steampy.utils import text_between


class Currency(enum.IntEnum):
    USD = 1
    GBP = 2
    EURO = 3
    CHF = 4


class GameOptions(enum.Enum):
    DOTA2 = ('570', '2')
    CS = ('730', '2')

    def __init__(self, app_id: str, context_id: str) -> None:
        self.app_id = app_id
        self.context_id = context_id


class TradeOfferState(enum.IntEnum):
    Invalid = 1
    Active = 2
    Accepted = 3
    Countered = 4
    Expired = 5
    Canceled = 6
    Declined = 7
    InvalidItems = 8
    ConfirmationNeed = 9
    CanceledBySecondaryFactor = 10
    StateInEscrow = 11


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

    def api_call(self, request_method: str, interface: str, api_method: str, version: str,
                 params: dict = None) -> requests.Response:
        url = '/'.join([self.API_URL, interface, api_method, version])
        if request_method == 'GET':
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, data=params)
        if self.is_invalid_api_key(response):
            raise InvalidCredentials('Invalid API key')
        return response

    @staticmethod
    def is_invalid_api_key(response: requests.Response) -> bool:
        msg = 'Access is denied. Retrying will not help. Please verify your <pre>key=</pre> parameter'
        return msg in response.text

    @login_required
    def get_my_inventory(self, game: GameOptions) -> dict:
        url = self.BASE_URL + '/my/inventory/json/' + \
              game.app_id + '/' + \
              game.context_id
        return self._session.get(url).json()

    def get_trade_offers_summary(self) -> dict:
        params = {'key': self._api_key}
        return self.api_call('GET', 'IEconService', 'GetTradeOffersSummary', 'v1', params).json()

    def get_trade_offers(self) -> dict:
        params = {'key': self._api_key,
                  'get_sent_offers': 1,
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
        partner = self._fetch_trade_partner_id(trade_offer_id)
        session_id = self._get_session_id()
        accept_url = self.BASE_URL + '/tradeoffer/' + trade_offer_id + '/accept'
        params = {'sessionid': session_id,
                  'tradeofferid': trade_offer_id,
                  'serverid': '1',
                  'partner': partner,
                  'captcha': ''}
        headers = {'Referer': self._get_trade_offer_url(trade_offer_id)}
        response = self._session.post(accept_url, data=params, headers=headers)
        if response.json().get('needs_mobile_confirmation', False):
            return ConfirmationExecutor(trade_offer_id, self.steam_guard['identity_secret'],
                                        self.steam_guard['steamid'], self._session).send_trade_allow_request()
        return response.json()

    def _get_trade_offer_url(self, trade_offer_id: str) -> str:
        return self.BASE_URL + '/tradeoffer/' + trade_offer_id

    def _get_session_id(self) -> str:
        return self._session.cookies.get_dict()['sessionid']

    def _fetch_trade_partner_id(self, trade_offer_id: str) -> dict:
        url = self._get_trade_offer_url(trade_offer_id)
        offer_response_text = self._session.get(url).text
        return text_between(offer_response_text, "var g_ulTradePartnerSteamID = '", "';")

    def decline_trade_offer(self, trade_offer_id: str) -> dict:
        params = {'key': self._api_key,
                  'tradeofferid': trade_offer_id}
        return self.api_call('POST', 'IEconService', 'DeclineTradeOffer', 'v1', params).json()

    def cancel_trade_offer(self, trade_offer_id: str) -> dict:
        params = {'key': self._api_key,
                  'tradeofferid': trade_offer_id}
        return self.api_call('POST', 'IEconService', 'CancelTradeOffer', 'v1', params).json()

    def fetch_price(self, item_hash_name: str, game: GameOptions, currency: str = Currency.USD) -> dict:
        url = self.BASE_URL + '/market/priceoverview/'
        params = {'country': 'PL',
                  'currency': currency,
                  'appid': game.app_id,
                  'market_hash_name': item_hash_name}
        return self._session.get(url, params=params).json()
