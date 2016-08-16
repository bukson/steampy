Steam Trade Offers Client for Python
=======

`steampy` is a library for Python, inspired by node-steam-tradeoffers, node-steam and other libraries for Node.js.
It was designed as a simple lightweight library, combining features of many steam libraries from Node.js into a single python module.
`steampy` is capable of logging into steam, fetching trade offers and handling them in simple manner, using steam user credentials
and SteamGuard file(no need to extract and pass sessionID and webCookie).
`steampy` is developed with Python 3 using type hints and many other features.

Installation
============

```
pip install steampy
```

Usage
=======
[Obtaining API Key](http://steamcommunity.com/dev/apikey)

[Obtaining SteamGuard from mobile device]( https://github.com/SMVampire/SteamBotDev/wiki )

[Obtaining SteamGuard using Android emulation]( https://github.com/codepath/android_guides/wiki/Genymotion-2.0-Emulators-with-Google-Play-support)

```
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
```

Examples
========

You'll need to install obtain your API key and SteamGuard file in order to run the examples, 
ant then fill login and password in `storehose.py` file.
The `storehouse.py` file contains an example of handling incoming trade offers.

```
python storehouse.py
```

Methods
=======

Unless specified in documentation, the method does not require login to work(it uses API Key from constructor instead)


**login(username: str, password: str, steam_guard: str) -> requests.Response**

Log into the steam account. Allows to accept trade offers and some other methods.

```
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
```

**api_call(request_method: str, interface: str, api_method: str, version: str, params: dict = None) -> requests.Response**

Directly call api method from the steam api services.

[Official steam api site](https://developer.valvesoftware.com/wiki/Steam_Web_API)

[Unofficial but more elegant](https://lab.xpaw.me/steam_api_documentation.html)

```
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
params = {'key': self._api_key}
summaries =  steam_client.api_call('GET', 'IEconService', 'GetTradeOffersSummary', 'v1', params).json()
```
**get_trade_offers_summary() -> dict**


**get_trade_offers() -> dict**

Fetching trade offers from steam using an API call.
Method is fetching offers with descriptions that satisfy conditions:
    * Are sent by us or others
    * Are active (means no historical, does not mean having offer state active!)
    * Are not historical
    * No time limitation
    
**get_trade_offer(trade_offer_id: str) -> dict**


**accept_trade_offer(trade_offer_id: str) -> dict**

Using `SteamClient.login` method is required before usage
This method also uses identity secret from SteamGuard file to confirm the trade offer.
No need to manually confirm it on mobile app or email.

**decline_trade_offer(trade_offer_id: str) -> dict**

Decline trade offer that **other** user sent to us.

**cancel_trade_offer(trade_offer_id: str) -> dict**

Cancel trade offer that **we** sent to other user.

**get_price(item_hash_name: str, game: GameOptions, currency: str = Currency.USD) -> dict**

Games are defined in GameOptions class, currently `GameOptions.DOTA2` and `GameOptions.CS`

Currencies are defined in Currency class, currently `Currency.USD`, `Currency.GBP`, `Currency.EURO`, `Currency.CHF`

Default currency is USD

```
client = SteamClient(self.credentials.api_key)
item = 'M4A1-S | Cyrex (Factory New)'
client.fetch_price(item, game=GameOptions.CS)
{'volume': '208', 'lowest_price': '$11.30 USD', 'median_price': '$11.33 USD', 'success': True}
```

**get_my_inventory(self, game: GameOptions) -> dict**

Using `SteamClient.login` method is required before usage

Test
====

All public methods are documented and tested. 
`guard` module has unit tests, `client` uses an acceptance test.
For the acceptance test you have to put `credentials.pwd` and `Steamguard` file into `test` directory.

Example `credentials.pwd` file:

```
account1 password1 api_key1
account2 password2 api_key2
```

In some tests you also have to obtain `transaction_id`.
You can do it by `SteamClient.get_trade_offers` or by logging manually into steam account in browser and get it from url

License
=======

MIT License

Copyright (c) 2016 [Michał Bukowski](gigibukson@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.