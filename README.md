Steam Trade Offers Client for Python
=======

[![PayPal Donate Button](https://img.shields.io/badge/donate-paypal-orange.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XC8BMJ8QRD9ZY "Donate to this project via PayPal")
[![Bitcoin Donate Button](https://img.shields.io/badge/donate-bitcoin-orange.svg)](https://blockchain.info/payment_request?address=1FxgPjRXx5es3qB5bpDtvqCwynWrMxnVim&message=Development+of+steampy&amount_local=5&currency=USD&nosavecurrency=true "Donate to this project via Bitcoin")

`steampy` is a library for Python, inspired by node-steam-tradeoffers, node-steam and other libraries for Node.js.
It was designed as a simple lightweight library, combining features of many steam libraries from Node.js into a single python module.
`steampy` is capable of logging into steam, fetching trade offers and handling them in simple manner, using steam user credentials
and SteamGuard file(no need to extract and pass sessionID and webCookie).
`steampy` is developed with Python 3 using type hints and many other features its supported for Windows, Linux and MacOs.

Table of Content
================

* [Installation](https://github.com/bukson/steampy#installation)

* [Usage](https://github.com/bukson/steampy#usage)

* [Examples](https://github.com/bukson/steampy#examples)

* [SteamClient methods](https://github.com/bukson/steampy#steamclient-methods)

* [Market methods](https://github.com/bukson/steampy#market-methods)

* [Guard module functions](https://github.com/bukson/steampy#guard-module-functions)

* [Test](https://github.com/bukson/steampy#test)

* [License](https://github.com/bukson/steampy#license)


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

```python
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
```

If you have `steamid`, `shared_secret` and `identity_secret` you can place it in file `Steamguard.txt` instead of fetching SteamGuard file from device.
```python
{
    "steamid": "YOUR_STEAM_ID_64",
    "shared_secret": "YOUR_SHARED_SECRET",
    "identity_secret": "YOUR_IDENTITY_SECRET",
}
```

Examples
========

You'll need to obtain your API key and SteamGuard file in order to run the examples, 
and then fill login and password in `storehose.py` file.
The `storehouse.py` file contains an example of handling incoming trade offers.

```
python storehouse.py
```

SteamClient methods
===================

Unless specified in documentation, the method does not require login to work(it uses API Key from constructor instead)


**login(username: str, password: str, steam_guard: str) -> requests.Response**

Log into the steam account. Allows to accept trade offers and some other methods.

```python
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
```

**logout() -> None**

Using `SteamClient.login` method is required before usage
Logout from steam.

```python
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
steam_client.logout()
```

**is_session_alive() -> None**

Using `SteamClient.login` method is required before usage
Check if session is alive. This method fetches main page and check
if user name is there. Thanks for vasia123 for this solution.

```python
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
is_session_alive = steam_client.is_session_alive()
```

**api_call(request_method: str, interface: str, api_method: str, version: str, params: dict = None) -> requests.Response**

Directly call api method from the steam api services.

[Official steam api site](https://developer.valvesoftware.com/wiki/Steam_Web_API)

[Unofficial but more elegant](https://lab.xpaw.me/steam_api_documentation.html)

```python
from steampy.client import SteamClient

steam_client = SteamClient('MY_API_KEY')
params = {'key': 'MY_API_KEY'}
summaries =  steam_client.api_call('GET', 'IEconService', 'GetTradeOffersSummary', 'v1', params).json()
```
**get_trade_offers_summary() -> dict**


**get_trade_offers(merge: bool = True) -> dict**

Fetching trade offers from steam using an API call.
Method is fetching offers with descriptions that satisfy conditions:

    * Are sent by us or others
    * Are active (means they have `trade_offer_state` set to 2 (Active))
    * Are not historical
    * No time limitation

If `merge` is set `True` then offer items are merged from items data and items description into dict where items `id` is key
and descriptions merged with data are value.

**get_trade_offer(trade_offer_id: str, merge: bool = True) -> dict**


**get_trade_receipt(trade_id: str) -> list**

Getting the receipt for a trade with all item information after the items has been traded.
Do NOT store any item ids before you got the receipt since the ids may change.
"trade_id" can be found in trade offers: `offer['response']['offer']['tradeid']`. Do not use ´tradeofferid´.


**make_offer(items_from_me: List[Asset], items_from_them: List[Asset], partner_steam_id: str, message:str ='') -> dict**

Using `SteamClient.login` method is required before usage
`Asset` is class defined in `client.py`, you can obtain `asset_id` from `SteamClient.get_my_inventory` method.
This method also uses identity secret from SteamGuard file to confirm the trade offer.
No need to manually confirm it on mobile app or email.
This method works when partner is your friend or steam.
In returned dict there will be trade offer id by the key `tradeofferid`.

```python
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions

steam_client = SteamClient('MY_API_KEY')
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
partner_id = 'PARTNER_ID'
game = GameOptions.CS
my_items = steam_client.get_my_inventory(game)
partner_items = steam_client.get_partner_inventory(partner_id, game)
my_first_item = next(iter(my_items.values()))
partner_first_item = next(iter(partner_items.values()))
my_asset = Asset(my_first_item['id'], game)
partner_asset = Asset(partner_first_item['id'], game)
steam_client.make_offer([my_asset], [partner_asset], partner_id, 'Test offer')
```

**make_offer_with_url(items_from_me: List[Asset], items_from_them: List[Asset], trade_offer_url: str, message: str = '') -> dict**

Using `SteamClient.login` method is required before usage
This method is similar to `SteamClient.make_offer`, but it takes trade url instead of friend account id.
It works even when partner isn't your steam friend
In returned dict there will be trade offer id by the key `tradeofferid`.

**get_escrow_duration(trade_offer_url: str) -> int**

Using `SteamClient.login` method is required before usage

Check the escrow duration for trade between you and partner(given partner trade offer url)

**accept_trade_offer(trade_offer_id: str) -> dict**

Using `SteamClient.login` method is required before usage
This method also uses identity secret from SteamGuard file to confirm the trade offer.
No need to manually confirm it on mobile app or email.

**decline_trade_offer(trade_offer_id: str) -> dict**

Decline trade offer that **other** user sent to us.

**cancel_trade_offer(trade_offer_id: str) -> dict**

Cancel trade offer that **we** sent to other user.

**get_my_inventory(game: GameOptions, merge: bool = True) -> dict**

Using `SteamClient.login` method is required before usage

If `merge` is set `True` then inventory items are merged from items data and items description into dict where items `id` is key
and descriptions merged with data are value.

Inventory entries looks like this:
```python
{'7146788981': {'actions': [{'link': 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S%owner_steamid%A%assetid%D316070896107169653',
                             'name': 'Inspect in Game...'}],
                'amount': '1',
                'appid': '730',
                'background_color': '',
                'classid': '1304827205',
                'commodity': 0,
                'contextid': '2',
                'descriptions': [{'type': 'html',
                                  'value': 'Exterior: Field-Tested'},
                                 {'type': 'html', 'value': ' '},
                                 {'type': 'html',
                                  'value': 'Powerful and reliable, the AK-47 '
                                           'is one of the most popular assault '
                                           'rifles in the world. It is most '
                                           'deadly in short, controlled bursts '
                                           'of fire. It has been painted using '
                                           'a carbon fiber hydrographic and a '
                                           'dry-transfer decal of a red '
                                           'pinstripe.\n'
                                           '\n'
                                           '<i>Never be afraid to push it to '
                                           'the limit</i>'},
                                 {'type': 'html', 'value': ' '},
                                 {'app_data': {'def_index': '65535',
                                               'is_itemset_name': 1},
                                  'color': '9da1a9',
                                  'type': 'html',
                                  'value': 'The Phoenix Collection'},
                                 {'type': 'html', 'value': ' '},
                                 {'app_data': {'def_index': '65535'},
                                  'type': 'html',
                                  'value': '<br><div id="sticker_info" '
                                           'name="sticker_info" title="Sticker '
                                           'Details" style="border: 2px solid '
                                           'rgb(102, 102, 102); border-radius: '
                                           '6px; width=100; margin:4px; '
                                           'padding:8px;"><center><img '
                                           'width=64 height=48 '
                                           'src="https://steamcdn-a.akamaihd.net/apps/730/icons/econ/stickers/eslkatowice2015/pentasports.a6b0ddffefb5507453456c0d2c35b6a57821c171.png"><img '
                                           'width=64 height=48 '
                                           'src="https://steamcdn-a.akamaihd.net/apps/730/icons/econ/stickers/eslkatowice2015/pentasports.a6b0ddffefb5507453456c0d2c35b6a57821c171.png"><img '
                                           'width=64 height=48 '
                                           'src="https://steamcdn-a.akamaihd.net/apps/730/icons/econ/stickers/eslkatowice2015/pentasports.a6b0ddffefb5507453456c0d2c35b6a57821c171.png"><img '
                                           'width=64 height=48 '
                                           'src="https://steamcdn-a.akamaihd.net/apps/730/icons/econ/stickers/cologne2015/mousesports.3e75da497d9f75fa56f463c22db25f29992561ce.png"><br>Sticker: '
                                           'PENTA Sports  | Katowice 2015, '
                                           'PENTA Sports  | Katowice 2015, '
                                           'PENTA Sports  | Katowice 2015, '
                                           'mousesports | Cologne '
                                           '2015</center></div>'}],
                'icon_drag_url': '',
                'icon_url': '-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhLsvQz',
                'icon_url_large': '-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5lpKKqPrxN7LEm1Rd6dd2j6eQ9N2t2wK3-ENsZ23wcIKRdQE2NwyD_FK_kLq9gJDu7p_KyyRr7nNw-z-DyIFJbNUz',
                'id': '7146788981',
                'instanceid': '480085569',
                'market_actions': [{'link': 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M%listingid%A%assetid%D316070896107169653',
                                    'name': 'Inspect in Game...'}],
                'market_hash_name': 'AK-47 | Redline (Field-Tested)',
                'market_name': 'AK-47 | Redline (Field-Tested)',
                'market_tradable_restriction': '7',
                'marketable': 1,
                'name': 'AK-47 | Redline',
                'name_color': 'D2D2D2',
                'owner_descriptions': '',
                'tags': [{'category': 'Type',
                          'category_name': 'Type',
                          'internal_name': 'CSGO_Type_Rifle',
                          'name': 'Rifle'},
                         {'category': 'Weapon',
                          'category_name': 'Weapon',
                          'internal_name': 'weapon_ak47',
                          'name': 'AK-47'},
                         {'category': 'ItemSet',
                          'category_name': 'Collection',
                          'internal_name': 'set_community_2',
                          'name': 'The Phoenix Collection'},
                         {'category': 'Quality',
                          'category_name': 'Category',
                          'internal_name': 'normal',
                          'name': 'Normal'},
                         {'category': 'Rarity',
                          'category_name': 'Quality',
                          'color': 'd32ce6',
                          'internal_name': 'Rarity_Legendary_Weapon',
                          'name': 'Classified'},
                         {'category': 'Exterior',
                          'category_name': 'Exterior',
                          'internal_name': 'WearCategory2',
                          'name': 'Field-Tested'},
                         {'category': 'Tournament',
                          'category_name': 'Tournament',
                          'internal_name': 'Tournament6',
                          'name': '2015 ESL One Katowice'},
                         {'category': 'Tournament',
                          'category_name': 'Tournament',
                          'internal_name': 'Tournament7',
                          'name': '2015 ESL One Cologne'},
                         {'category': 'TournamentTeam',
                          'category_name': 'Team',
                          'internal_name': 'Team39',
                          'name': 'PENTA Sports'},
                         {'category': 'TournamentTeam',
                          'category_name': 'Team',
                          'internal_name': 'Team29',
                          'name': 'mousesports'}],
                'tradable': 1,
                'type': 'Classified Rifle'}}
```

**get_partner_inventory(partner_steam_id: str, game: GameOptions, merge: bool = True) -> dict**

Using `SteamClient.login` method is required before usage

Inventory items can be merged like in `SteamClient.get_my_inventory` method

market methods
==============

**fetch_price(item_hash_name: str, game: GameOptions, currency: str = Currency.USD) -> dict**

Games are defined in GameOptions class, currently `GameOptions.DOTA2`, `GameOptions.CS` and `GameOptions.TF2`

Currencies are defined in Currency class, currently `Currency.USD`, `Currency.GBP`, `Currency.EURO`, `Currency.CHF`

Default currency is USD

May rise `TooManyRequests` exception if used more than 20 times in 60 seconds.

```python
client = SteamClient(self.credentials.api_key)
item = 'M4A1-S | Cyrex (Factory New)'
client.market.fetch_price(item, game=GameOptions.CS)
{'volume': '208', 'lowest_price': '$11.30 USD', 'median_price': '$11.33 USD', 'success': True}
```


**get_my_market_listings() -> dict**

Using `SteamClient.login` method is required before usage

Returns market listings posted by user

```python
client = SteamClient(self.credentials.api_key)
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
listings = client.market.get_my_market_listings()
```


**create_sell_order(assetid: str, game: GameOptions, money_to_receive: str) -> dict**

Using `SteamClient.login` method is required before usage

Create sell order of the asset on the steam market.

```python
client = SteamClient(self.credentials.api_key)
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
asset_id_to_sell = 'some_asset_id'
game = GameOptions.DOTA2
sell_response = client.market.create_sell_order(asset_id_to_sell, game, "10000")
```
 
**create_buy_order(market_name: str, price_single_item: str, quantity: int, game: GameOptions, currency: Currency = Currency.USD) -> dict**

Using `SteamClient.login` method is required before usage

Create buy order of the assets on the steam market.

```python
client = SteamClient(self.credentials.api_key)
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
response = client.market.create_buy_order("AK-47 | Redline (Field-Tested)", "10.34", 2, GameOptions.CS, Currency.EURO)
buy_order_id = response["buy_orderid"]
```

**cancel_sell_order(sell_listing_id: str) -> None**

Using `SteamClient.login` method is required before usage

Cancel previously requested sell order on steam market.

```python
client = SteamClient(self.credentials.api_key)
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
sell_order_id = "some_sell_order_id"
response = client.market.cancel_sell_order(sell_order_id)
```

**cancel_buy_order(buy_order_id) -> dict**

Using `SteamClient.login` method is required before usage

Cancel previously requested buy order on steam market.

```python
client = SteamClient(self.credentials.api_key)
steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE')
buy_order_id = "some_buy_order_id"
response = client.market.cancel_buy_order(buy_order_id)
```

guard module functions
======================

**load_steam_guard(steam_guard: str) -> dict**

If `steam_guard` is file name then load and parse it, else just parse `steam_guard` as json string.

**generate_one_time_code(shared_secret: str, timestamp: int = None) -> str**

Generate one time code for logging into Steam using shared_secret from SteamGuard file.
If none timestamp provided, timestamp will be set to current time.

**generate_confirmation_key(identity_secret: str, tag: str, timestamp: int = int(time.time())) -> bytes**

Generate mobile device confirmation key for accepting trade offer. 
Default timestamp is current time.

Test
====

All public methods are documented and tested. 
`guard` module has unit tests, `client` uses an acceptance test.
For the acceptance test you have to put `credentials.pwd` and `Steamguard` file into `test` directory

Example `credentials.pwd` file:

```
account1 password1 api_key1
account2 password2 api_key2
```

In some tests you also have to obtain `transaction_id`.
You can do it by `SteamClient.get_trade_offers` or by logging manually into steam account in browser and get it from url

In some tests you also have to obtain partner steam id.
You can do it by by logging manually into steam account in browser and get it from url

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
