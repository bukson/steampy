import base64
import time

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from steampy import guard


class LoginExecutor:
    COMMUNITY_URL = "https://steamcommunity.com"

    def __init__(self, username: str, password: str, shared_secret: str, session: requests.Session) -> None:
        self.username = username
        self.password = password
        self.one_time_code = ''
        self.shared_secret = shared_secret
        self.session = session

    def login(self) -> requests.Session:
        login_response = self._send_login_request()
        self._check_for_captcha(login_response)
        login_response = self._enter_steam_guard_if_necessary(login_response)
        self._perform_redirects(login_response.json())
        return self.session

    def _send_login_request(self) -> requests.Response:
        rsa_params = self._fetch_rsa_params()
        encrypted_password = self._encrypt_password(rsa_params)
        rsa_timestamp = rsa_params['rsa_timestamp']
        request_data = self._prepare_login_request_data(encrypted_password, rsa_timestamp)
        return self.session.post(self.COMMUNITY_URL + '/login/dologin', data=request_data)

    def _fetch_rsa_params(self) -> dict:
        key_response = self.session.post(self.COMMUNITY_URL + '/login/getrsakey/',
                                         data={'username': self.username}).json()
        rsa_mod = int(key_response['publickey_mod'], 16)
        rsa_exp = int(key_response['publickey_exp'], 16)
        rsa_timestamp = key_response['timestamp']
        return {'rsa_key': RSA.construct((rsa_mod, rsa_exp)),
                'rsa_timestamp': rsa_timestamp}

    def _encrypt_password(self, rsa_params: dict) -> str:
        return base64.b64encode(
            PKCS1_v1_5.new(rsa_params['rsa_key']).encrypt(self.password.encode('utf-8')))

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
            'remember_login': 'false',
            'donotcache': str(int(time.time() * 1000))
        }

    @staticmethod
    def _check_for_captcha(login_response: requests.Response) -> None:
        if login_response.json().get('captcha_needed', False):
            raise CaptchaRequired('Captcha required')

    def _enter_steam_guard_if_necessary(self, login_response: requests.Response) -> requests.Response:
        if login_response.json()['requires_twofactor']:
            self.one_time_code = guard.generate_one_time_code(self.shared_secret)
            return self._send_login_request()
        return login_response

    @staticmethod
    def _assert_valid_credentials(login_response: requests.Response) -> None:
        if not login_response.json()['success']:
            raise InvalidCredentials(login_response.json()['message'])

    def _perform_redirects(self, response_dict: dict) -> requests.Response:
        parameters = response_dict['transfer_parameters']
        for url in response_dict['transfer_urls']:
            self.session.post(url, parameters)

    def _fetch_home_page(self, session: requests.Session) -> requests.Response:
        return session.post(self.COMMUNITY_URL + '/my/home/')


class InvalidCredentials(Exception):
    pass


class CaptchaRequired(Exception):
    pass
