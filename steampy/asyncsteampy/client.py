import decimal

import bs4
import urllib.parse as urlparse
from typing import List, Union

import json
import aiohttp
from steampy import guard
from steampy.asyncsteampy.chat import SteamChat
from steampy.asyncsteampy.confirmation import ConfirmationExecutor
from steampy.exceptions import SevenDaysHoldException, LoginRequired, ApiException
from steampy.asyncsteampy.login import LoginExecutor, InvalidCredentials
from steampy.asyncsteampy.market import SteamMarket
from steampy.models import Asset, TradeOfferState, SteamUrl, GameOptions
from steampy.utils import text_between, texts_between, merge_items_with_descriptions_from_inventory, \
    steam_id_to_account_id, merge_items_with_descriptions_from_offers, get_description_key, \
    merge_items_with_descriptions_from_offer, account_id_to_steam_id, get_key_value_from_url, parse_price, get_sessionid_from_cookie


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if not self.was_login_executed:
            raise LoginRequired('Use login method first')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


class SteamClient:
    def __init__(self, api_key: str, username: str = None, password: str = None, steam_guard: str = None) -> None:
        self._api_key = api_key
        self._session = aiohttp.ClientSession()
        self.steam_guard = steam_guard
        self.was_login_executed = False
        self.username = username
        self._password = password
        self.market = SteamMarket(self._session)
        self.chat = SteamChat(self._session)

    async def login(self, username: str, password: str, steam_guard: str) -> None:
        self.steam_guard = guard.load_steam_guard(steam_guard)
        self.username = username
        self._password = password
        await LoginExecutor(username, password, self.steam_guard['shared_secret'], self._session).login()
        self.was_login_executed = True
        self.market._set_login_executed(self.steam_guard, get_sessionid_from_cookie(self._session.cookie_jar))

    @login_required
    async def logout(self) -> None:
        url = SteamUrl.STORE_URL + '/login/logout/'
        data = {'sessionid': get_sessionid_from_cookie(self._session.cookie_jar)}
        await self._session.post(url, data=data)
        if await self.is_session_alive():
            raise Exception("Logout unsuccessful")
        self.was_login_executed = False

    async def close(self) -> None:
        if self.was_login_executed:
            await self.logout()
        await self._session.close()

    async def __aenter__(self):
        if None in [self.username, self._password, self.steam_guard]:
            raise InvalidCredentials('You have to pass username, password and steam_guard'
                                     'parameters when using "with" statement')
        await self.login(self.username, self._password, self.steam_guard)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()
        await self.close()

    @login_required
    async def is_session_alive(self):
        steam_login = self.username
        main_page_response = await self._session.get(SteamUrl.COMMUNITY_URL)
        main_page_response_text = await main_page_response.text()
        return steam_login.lower() in main_page_response_text.lower()

    async def api_call(self, request_method: str, interface: str, api_method: str, version: str,
                 params: dict = None) -> aiohttp.ClientResponse:
        url = '/'.join([SteamUrl.API_URL, interface, api_method, version])
        async with aiohttp.ClientSession() as session:
            if request_method == 'GET':
                response = await session.get(url, params=params)
            else:
                response = await session.post(url, data=params)
            await response.read()
        if self._is_invalid_api_key(await response.text()):
            raise InvalidCredentials('Invalid API key')
        return response

    @staticmethod
    def _is_invalid_api_key(response_text: str) -> bool:
        msg = 'Access is denied. Retrying will not help. Please verify your <pre>key=</pre> parameter'
        return msg in response_text

    @login_required
    async def get_my_inventory(self, game: GameOptions, merge: bool = True, count: int = 5000) -> dict:
        steam_id = self.steam_guard['steamid']
        return await self.get_partner_inventory(steam_id, game, merge, count)

    @login_required
    async def get_partner_inventory(self, partner_steam_id: str, game: GameOptions, merge: bool = True, count: int = 5000) -> dict:
        url = '/'.join([SteamUrl.COMMUNITY_URL, 'inventory', partner_steam_id, game.app_id, game.context_id])
        params = {'l': 'english',
                  'count': count}
        response = await self._session.get(url, params=params)
        response_dict: dict = await response.json()
        if response_dict['success'] != 1:
            raise ApiException('Success value should be 1.')
        if merge:
            return merge_items_with_descriptions_from_inventory(response_dict, game)
        return response_dict

    async def get_trade_offers_summary(self) -> dict:
        params = {'key': self._api_key}
        response = await self.api_call('GET', 'IEconService', 'GetTradeOffersSummary', 'v1', params)
        return await response.json()

    async def get_trade_offers(self, merge: bool = True) -> dict:
        params = {'key': self._api_key,
                  'get_sent_offers': 1,
                  'get_received_offers': 1,
                  'get_descriptions': 1,
                  'language': 'english',
                  'active_only': 1,
                  'historical_only': 0,
                  'time_historical_cutoff': ''}
        response = await self.api_call('GET', 'IEconService', 'GetTradeOffers', 'v1', params)
        response_json = await response.json()
        response_json = self._filter_non_active_offers(response_json)
        if merge:
            response_json = merge_items_with_descriptions_from_offers(response_json)
        return response_json

    @staticmethod
    def _filter_non_active_offers(offers_response: dict) -> dict:
        offers_received = offers_response['response'].get('trade_offers_received', [])
        offers_sent = offers_response['response'].get('trade_offers_sent', [])
        offers_response['response']['trade_offers_received'] = list(
            filter(lambda offer: offer['trade_offer_state'] == TradeOfferState.Active, offers_received))
        offers_response['response']['trade_offers_sent'] = list(
            filter(lambda offer: offer['trade_offer_state'] == TradeOfferState.Active, offers_sent))
        return offers_response

    async def get_trade_offer(self, trade_offer_id: str, merge: bool = True) -> dict:
        params = {'key': self._api_key,
                  'tradeofferid': trade_offer_id,
                  'language': 'english'}
        response = await self.api_call('GET', 'IEconService', 'GetTradeOffer', 'v1', params)
        response_json = await response.json()
        if merge and "descriptions" in response_json['response']:
            descriptions = {get_description_key(offer): offer for offer in response_json['response']['descriptions']}
            offer = response_json['response']['offer']
            response_json['response']['offer'] = merge_items_with_descriptions_from_offer(offer, descriptions)
        return response_json

    async def get_trade_history(self,
                          max_trades=100,
                          start_after_time=None,
                          start_after_tradeid=None,
                          get_descriptions=True,
                          navigating_back=True,
                          include_failed=True,
                          include_total=True) -> dict:
        params = {
            'key': self._api_key,
            'max_trades': max_trades,
            'start_after_time': start_after_time,
            'start_after_tradeid': start_after_tradeid,
            'get_descriptions': get_descriptions,
            'navigating_back': navigating_back,
            'include_failed': include_failed,
            'include_total': include_total
        }
        response = await self.api_call('GET', 'IEconService', 'GetTradeHistory', 'v1', params)
        response_json = await response.json()
        return response_json

    @login_required
    async def get_trade_receipt(self, trade_id: str) -> list:
        response = await self._session.get("https://steamcommunity.com/trade/{}/receipt".format(trade_id))
        content = await response.content.read()
        html = content.decode()
        items = []
        for item in texts_between(html, "oItem = ", ";\r\n\toItem"):
            items.append(json.loads(item))
        return items

    @login_required
    async def accept_trade_offer(self, trade_offer_id: str) -> dict:
        trade = await self.get_trade_offer(trade_offer_id)
        trade_offer_state = TradeOfferState(trade['response']['offer']['trade_offer_state'])
        if trade_offer_state is not TradeOfferState.Active:
            raise ApiException("Invalid trade offer state: {} ({})".format(trade_offer_state.name,
                                                                           trade_offer_state.value))
        partner = self._fetch_trade_partner_id(trade_offer_id)
        session_id = get_sessionid_from_cookie(self._session.cookie_jar)
        accept_url = SteamUrl.COMMUNITY_URL + '/tradeoffer/' + trade_offer_id + '/accept'
        params = {'sessionid': session_id,
                  'tradeofferid': trade_offer_id,
                  'serverid': '1',
                  'partner': partner,
                  'captcha': ''}
        headers = {'Referer': self._get_trade_offer_url(trade_offer_id)}
        response = await self._session.post(accept_url, data=params, headers=headers)
        response_json = await response.json()
        if response_json.get('needs_mobile_confirmation', False):
            return await self._confirm_transaction(trade_offer_id)
        return response_json

    def _fetch_trade_partner_id(self, trade_offer_id: str) -> str:
        url = self._get_trade_offer_url(trade_offer_id)
        offer_response_text = self._session.get(url).text
        if 'You have logged in from a new device. In order to protect the items' in offer_response_text:
            raise SevenDaysHoldException("Account has logged in a new device and can't trade for 7 days")
        return text_between(offer_response_text, "var g_ulTradePartnerSteamID = '", "';")

    async def _confirm_transaction(self, trade_offer_id: str) -> dict:
        confirmation_executor = ConfirmationExecutor(self.steam_guard['identity_secret'], self.steam_guard['steamid'],
                                                     self._session)
        return await confirmation_executor.send_trade_allow_request(trade_offer_id)

    async def decline_trade_offer(self, trade_offer_id: str) -> dict:
        url = 'https://steamcommunity.com/tradeoffer/' + trade_offer_id + '/decline'
        response = await self._session.post(url, data={'sessionid': get_sessionid_from_cookie(self._session.cookie_jar)})
        response_json = await response.json()
        return response_json

    async def cancel_trade_offer(self, trade_offer_id: str) -> dict:
        url = 'https://steamcommunity.com/tradeoffer/' + trade_offer_id + '/cancel'
        response = await self._session.post(url, data={'sessionid': get_sessionid_from_cookie(self._session.cookie_jar)})
        response_json = await response.json()
        return response_json
    
    @login_required
    async def make_offer(self, items_from_me: List[Asset], items_from_them: List[Asset], partner_steam_id: str,
                   message: str = '') -> dict:
        offer = self._create_offer_dict(items_from_me, items_from_them)
        session_id = get_sessionid_from_cookie(self._session.cookie_jar)
        url = SteamUrl.COMMUNITY_URL + '/tradeoffer/new/send'
        server_id = 1
        params = {
            'sessionid': session_id,
            'serverid': server_id,
            'partner': partner_steam_id,
            'tradeoffermessage': message,
            'json_tradeoffer': json.dumps(offer),
            'captcha': '',
            'trade_offer_create_params': '{}'
        }
        partner_account_id = steam_id_to_account_id(partner_steam_id)
        headers = {'Referer': SteamUrl.COMMUNITY_URL + '/tradeoffer/new/?partner=' + partner_account_id,
                   'Origin': SteamUrl.COMMUNITY_URL}
        response = await self._session.post(url, data=params, headers=headers)
        response_json: dict = await response.json()
        if response_json.get('needs_mobile_confirmation'):
            response_json.update(await self._confirm_transaction(response_json['tradeofferid']))
        return response_json

    async def get_profile(self, steam_id: str) -> dict:
        params = {'steamids': steam_id, 'key': self._api_key}
        response = await self.api_call('GET', 'ISteamUser', 'GetPlayerSummaries', 'v0002', params)
        data = await response.json()
        return data['response']['players'][0]

    async def get_friend_list(self, steam_id: str, relationship_filter: str="all") -> dict:
        params = {
            'key': self._api_key,
            'steamid': steam_id,
            'relationship': relationship_filter
        }
        response = await self.api_call("GET", "ISteamUser", "GetFriendList", "v1", params)
        data = await response.json()
        return data['friendslist']['friends']

    @staticmethod
    def _create_offer_dict(items_from_me: List[Asset], items_from_them: List[Asset]) -> dict:
        return {
            'newversion': True,
            'version': 4,
            'me': {
                'assets': [asset.to_dict() for asset in items_from_me],
                'currency': [],
                'ready': False
            },
            'them': {
                'assets': [asset.to_dict() for asset in items_from_them],
                'currency': [],
                'ready': False
            }
        }

    @login_required
    async def get_escrow_duration(self, trade_offer_url: str) -> int:
        headers = {'Referer': SteamUrl.COMMUNITY_URL + urlparse.urlparse(trade_offer_url).path,
                   'Origin': SteamUrl.COMMUNITY_URL}
        response = await self._session.get(trade_offer_url, headers=headers)
        response_text = await response.text()
        my_escrow_duration = int(text_between(response_text, "var g_daysMyEscrow = ", ";"))
        their_escrow_duration = int(text_between(response_text, "var g_daysTheirEscrow = ", ";"))
        return max(my_escrow_duration, their_escrow_duration)

    @login_required
    async def make_offer_with_url(self, items_from_me: List[Asset], items_from_them: List[Asset],
                            trade_offer_url: str, message: str = '', case_sensitive: bool=True) -> dict:
        token = get_key_value_from_url(trade_offer_url, 'token', case_sensitive)
        partner_account_id = get_key_value_from_url(trade_offer_url, 'partner', case_sensitive)
        partner_steam_id = account_id_to_steam_id(partner_account_id)
        offer = self._create_offer_dict(items_from_me, items_from_them)
        session_id = get_sessionid_from_cookie(self._session.cookie_jar)
        url = SteamUrl.COMMUNITY_URL + '/tradeoffer/new/send'
        server_id = 1
        trade_offer_create_params = {'trade_offer_access_token': token}
        params = {
            'sessionid': session_id,
            'serverid': server_id,
            'partner': partner_steam_id,
            'tradeoffermessage': message,
            'json_tradeoffer': json.dumps(offer),
            'captcha': '',
            'trade_offer_create_params': json.dumps(trade_offer_create_params)
        }
        headers = {'Referer': SteamUrl.COMMUNITY_URL + urlparse.urlparse(trade_offer_url).path,
                   'Origin': SteamUrl.COMMUNITY_URL}
        response = await self._session.post(url, data=params, headers=headers)
        response_json: dict = await response.json()

        if response_json.get('needs_mobile_confirmation'):
            response_json.update(await self._confirm_transaction(response_json['tradeofferid']))
        return response_json

    @staticmethod
    def _get_trade_offer_url(trade_offer_id: str) -> str:
        return SteamUrl.COMMUNITY_URL + '/tradeoffer/' + trade_offer_id

    @login_required
    async def get_wallet_balance(self, convert_to_decimal: bool = True) -> Union[str, decimal.Decimal]:
        url = SteamUrl.STORE_URL + '/account/history/'
        response = await self._session.get(url)
        response_soup = bs4.BeautifulSoup(await response.text(), "html.parser")
        balance = response_soup.find(id='header_wallet_balance').string
        if convert_to_decimal:
            return parse_price(balance)
        else:
            return balance
