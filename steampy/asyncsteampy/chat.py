import bs4
import re
import aiohttp
from steampy.models import Endpoints, SteamUrl
from steampy.utils import account_id_to_steam_id


class SteamChat():

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._chat_params = {}

    async def _get_access_token(self):
        response = await self._session.get(SteamUrl.COMMUNITY_URL + "/chat")
        response.raise_for_status()
        response_soup = bs4.BeautifulSoup(await response.text(), "html.parser")
        elems = response_soup.select("body > div > div > div > script[type]")
        token_pattern = re.compile(r"\"(\w{32})\"")
        access_token = token_pattern.search(str(elems[0])).group(1)
        if access_token is None:
            raise Exception("Failed to retrieve the access_token")
        else:
            return access_token

    async def _api_call(self, endpoint, params, timeout_ignore=False) -> aiohttp.ClientResponse:
        response = await self._session.post(endpoint, data=params)
        response.raise_for_status()
        await response.read()
        response_json: dict = await response.json()
        response_status = response_json.get("error")
        if timeout_ignore and response_status == "Timeout":
            return
        elif response_status != "OK":
            raise Exception(response_status)
        else:
            return response

    async def _login(self, ui_mode="web") -> aiohttp.ClientResponse:
        self._chat_params["ui_mode"] = ui_mode
        self._chat_params["access_token"] = self._get_access_token()
        endpoint = Endpoints.CHAT_LOGIN
        params = {"ui_mode": self._chat_params.get("ui_mode"),
                  "access_token": self._chat_params.get("access_token")}
        response = await self._api_call(endpoint, params)
        await response.read()
        self._chat_params.update(await response.json())
        return response

    async def _logout(self) -> aiohttp.ClientResponse:
        endpoint = Endpoints.CHAT_LOGOUT
        params = {"access_token": self._chat_params.get("access_token"),
                  "umqid": self._chat_params.get("umqid")}
        self._chat_params = {}
        return await self._api_call(endpoint, params)

    async def send_message(self, steamid_64, text) -> aiohttp.ClientResponse:
        endpoint = Endpoints.SEND_MESSAGE
        params = {"access_token": self._chat_params.get("access_token"),
                  "steamid_dst": steamid_64,
                  "text": text,
                  "type": "saytext",
                  "umqid": self._chat_params.get("umqid")}
        return await self._api_call(endpoint, params)

    async def poll_events(self) -> dict:
        endpoint = Endpoints.CHAT_POLL
        params = {"access_token": self._chat_params.get("access_token"),
                  "umqid": self._chat_params.get("umqid"),
                  "message": self._chat_params.get("message"),
                  "pollid": 1,
                  "sectimeout": 20,
                  "secidletime": 0,
                  "use_accountids": 1}
        response = await self._api_call(endpoint, params, timeout_ignore=True)
        if not response:
            return {}
        data = await response.json()
        self._chat_params["message"] = data["messagelast"]
        return data

    async def fetch_messages(self) -> dict:
        message_list = {
            'sent': [],
            'received': []
        }
        events = await self.poll_events()
        if not events:
            return message_list
        messages = events["messages"]
        for message in messages:
            text = message.get("text")
            if message['type'] == "saytext":
                accountid_from = account_id_to_steam_id(message.get("accountid_from"))
                message_list['received'].append({"partner": accountid_from, "message": text})
            elif message['type'] == "my_saytext":
                accountid_from = account_id_to_steam_id(message.get("accountid_from"))
                message_list['sent'].append({"partner": accountid_from, "message": text})
        return message_list
