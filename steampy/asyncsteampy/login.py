import base64
import time
import aiohttp
from yarl import URL
from steampy import guard
import rsa
from steampy.models import SteamUrl
from steampy.exceptions import InvalidCredentials, CaptchaRequired
from steampy.utils import get_sessionid_from_cookie


class LoginExecutor:

    def __init__(self, username: str, password: str, shared_secret: str, session: aiohttp.ClientSession) -> None:
        self.username = username
        self.password = password
        self.one_time_code = ''
        self.shared_secret = shared_secret
        self.session = session

    async def login(self) -> aiohttp.ClientSession:
        login_response_json = await self._send_login_request()
        self._check_for_captcha(login_response_json)
        login_response_json = await self._enter_steam_guard_if_necessary(login_response_json)
        self._assert_valid_credentials(login_response_json)
        await self._perform_redirects(login_response_json)
        self._set_sessionid_cookies()
        return self.session

    async def _send_login_request(self) -> dict:
        rsa_params = await self._fetch_rsa_params()
        encrypted_password = self._encrypt_password(rsa_params)
        rsa_timestamp = rsa_params['rsa_timestamp']
        request_data = self._prepare_login_request_data(encrypted_password, rsa_timestamp)
        response = await self.session.post(SteamUrl.STORE_URL + '/login/dologin', data=request_data)
        return await response.json()

    def _set_sessionid_cookies(self):
        sessionid = get_sessionid_from_cookie(self.session.cookie_jar)
        community_domain = SteamUrl.COMMUNITY_URL[8:]
        store_domain = SteamUrl.STORE_URL[8:]
        community_cookie = self._create_session_id_cookie(sessionid, community_domain)
        store_cookie = self._create_session_id_cookie(sessionid, store_domain)
        self.session.cookie_jar.update_cookies(**community_cookie)
        self.session.cookie_jar.update_cookies(**store_cookie)

    @staticmethod
    def _create_session_id_cookie(sessionid: str, domain: str) -> dict:
        return {"cookies": {"sessionid": sessionid},
                "response_url": URL(domain)}

    async def _fetch_rsa_params(self, current_number_of_repetitions: int = 0) -> dict:
        maximal_number_of_repetitions = 5
        response = await self.session.post(SteamUrl.STORE_URL + '/login/getrsakey/',
                                         data={'username': self.username})
        key_response = await response.json()
        try:
            rsa_mod = int(key_response['publickey_mod'], 16)
            rsa_exp = int(key_response['publickey_exp'], 16)
            rsa_timestamp = key_response['timestamp']
            return {'rsa_key': rsa.PublicKey(rsa_mod, rsa_exp),
                    'rsa_timestamp': rsa_timestamp}
        except KeyError:
            if current_number_of_repetitions < maximal_number_of_repetitions:
                return await self._fetch_rsa_params(current_number_of_repetitions + 1)
            else:
                raise ValueError('Could not obtain rsa-key')

    def _encrypt_password(self, rsa_params: dict) -> str:
        return base64.b64encode(rsa.encrypt(self.password.encode('utf-8'), rsa_params['rsa_key'])).decode()

    def _prepare_login_request_data(self, encrypted_password: str, rsa_timestamp: str) -> dict:
        return {
            'password': encrypted_password,
            'username': self.username,
            'twofactorcode': self.one_time_code,
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': rsa_timestamp,
            'remember_login': 'true',
            'donotcache': str(int(time.time() * 1000))
        }

    @staticmethod
    def _check_for_captcha(login_response: dict) -> None:
        if login_response.get('captcha_needed', False):
            raise CaptchaRequired('Captcha required')

    async def _enter_steam_guard_if_necessary(self, login_response: dict) -> dict:
        if login_response['requires_twofactor']:
            self.one_time_code = guard.generate_one_time_code(self.shared_secret)
            return await self._send_login_request()
        return login_response

    @staticmethod
    def _assert_valid_credentials(login_response: dict) -> None:
        if not login_response['success']:
            raise InvalidCredentials(login_response['message'])

    async def _perform_redirects(self, response_dict: dict) -> None:
        parameters = response_dict.get('transfer_parameters')
        if parameters is None:
            raise Exception('Cannot perform redirects after login, no parameters fetched')
        for url in response_dict['transfer_urls']:
            await self.session.post(url=url, data=parameters)

    async def _fetch_home_page(self, session: aiohttp.ClientSession) -> aiohttp.ClientResponse:
        return await session.post(SteamUrl.COMMUNITY_URL + '/my/home/')
