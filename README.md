Steam Trade Offers Client for Python
=======

`steampy` is a library for Python, inspired by node-steam-tradeoffers, node-steam and others libraries for Node.js.
It was designed simple lightweight library, combining features of many steam libraries from Node.js in one python module.
`steampy` is capable of logging to steam, fetching trade offers and handle them in simple manner, using steam user credentials
and SteamGuard file(no need to extract and pass sessionID and webCookie).
`steampy` is developed with Python 3 using type hints and many other features.

Installation
============

TODO add to pip

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

Demo
====
TODO

Examples
========
TODO

Methods
=======

If not specified in documentation, method does not require login to work(it uses API Key from constructor instead)


login(username: str, password: str, steam_guard: str) -> requests.Response
-------------------------------------------------------------------------


api_call(request_method: str, interface: str, api_method: str, version: str, params: dict = None) -> requests.Response
----------------------------------------------------------------------------------------------------------------------

get_trade_offers_summary() -> dict
----------------------------------

get_trade_offers() -> dict
--------------------------

get_trade_offer(trade_offer_id: str) -> dict
--------------------------------------------

accept_trade_offer(trade_offer_id: str) -> dict
-----------------------------------------------

using `SteamClient.login` method is required before usage

decline_trade_offer(trade_offer_id: str) -> dict
------------------------------------------------

cancel_trade_offer(trade_offer_id: str) -> dict
-----------------------------------------------

get_price(item_hash_name: str, game: GameOptions, currency: str = Currency.USD) -> dict
---------------------------------------------------------------------------------------
Probably can be used without logging into Steam

Games are defined in GameOptions class, currently `GameOptions.DOTA2` and `GameOptions.CS`

Currencies are defined in Currency class, currently `Currency.USD`, `Currency.GBP`, `Currency.EURO`, `Currency.CHF`

Default currency is USD

Test
====

TODO

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