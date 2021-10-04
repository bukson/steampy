Asyncio
====

All methods that requires connection to steam network now have asyncio support (it uses [aiohttp]( https://github.com/aio-libs/aiohttp) ) and are asynchronous : `client`, `market`, `chat`.

```python
from steampy.asyncsteampy.client import SteamClient as AsyncSteamClient

...

async_steam_client = await AsyncSteamClient(self.credentials.api_key)
await async_steam_client.login('MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE/DICT')
buy_order_id = "some_buy_order_id"
response = await steam_client.market.cancel_buy_order(buy_order_id)

await async_steam_client.close()
```

If you end your operations, ceep in mind, you always need to `close` your `async_steam_client`. This will do `logout` and close `aiohttp` [session]( https://docs.aiohttp.org/en/stable/client_reference.html#client-session) properly. Also, you can `await async_steam_client.logout()` without closing session if you need this for some reason.

Async context manager usage example:

```python
async with AsyncSteamClient(self.credentials.api_key,'MY_USERNAME', 'MY_PASSWORD', 'PATH_TO_STEAMGUARD_FILE/DICT') as async_steam_client:
    await async_steam_client.do_what_you_need()

```

There you no need to call `close`, async context manager do it automatically when execution passes the block of code.