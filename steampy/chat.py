import bs4
import re
from steampy.models import Endpoints, SteamUrl
from steampy.utils import account_id_to_steam_id


class SteamChat():

    def __init__(self, session):
        self._session = session
        self._chat_params = {}

    def _get_access_token(self):
        response = self._session.get(SteamUrl.COMMUNITY_URL + "/chat")
        response.raise_for_status()
        response_soup = bs4.BeautifulSoup(response.text, "html.parser")
        elems = response_soup.select("body > div > div > div > script[type]")
        token_pattern = re.compile(r"\"(\w{32})\"")
        access_token = token_pattern.search(str(elems[0])).group(1)
        if access_token is None:
            raise Exception("Failed to retrieve the access_token")
        else:
            return access_token

    def _api_call(self, endpoint, params, timeout_ignore=False):
        response = self._session.post(endpoint, data=params)
        response.raise_for_status()
        response_status = response.json().get("error")
        if timeout_ignore and response_status == "Timeout":
            return
        elif response_status != "OK":
            raise Exception(response_status)
        else:
            return response

    def _login(self, ui_mode="web"):
        self._chat_params["ui_mode"] = ui_mode
        self._chat_params["access_token"] = self._get_access_token()
        endpoint = Endpoints.CHAT_LOGIN
        params = {"ui_mode": self._chat_params.get("ui_mode"),
                  "access_token": self._chat_params.get("access_token")}
        response = self._api_call(endpoint, params)
        self._chat_params.update(response.json())
        return response

    def _logout(self):
        endpoint = Endpoints.CHAT_LOGOUT
        params = {"access_token": self._chat_params.get("access_token"),
                  "umqid": self._chat_params.get("umqid")}
        self._chat_params = {}
        return self._api_call(endpoint, params)

    def send_message(self, steamid_64, text):
        endpoint = Endpoints.SEND_MESSAGE
        params = {"access_token": self._chat_params.get("access_token"),
                  "steamid_dst": steamid_64,
                  "text": text,
                  "type": "saytext",
                  "umqid": self._chat_params.get("umqid")}
        return self._api_call(endpoint, params)

    def chat_poll(self):
        endpoint = Endpoints.CHAT_POLL
        params = {"access_token": self._chat_params.get("access_token"),
                  "umqid": self._chat_params.get("umqid"),
                  "message": self._chat_params.get("message"),
                  "pollid": 1,
                  "sectimeout": 20,
                  "secidletime": 0,
                  "use_accountids": 1}
        response = self._api_call(endpoint, params, timeout_ignore=True)
        if response is None:
            return []
        self._chat_params["message"] = response.json().get("messagelast")
        messages = response.json().get("messages")
        message_list = []
        for message in messages:
            text = message.get("text")
            if text:
                accountid_from = account_id_to_steam_id(message.get("accountid_from"))
                message_list.append({"from": accountid_from, "message": text})
        return message_list
