import json

from steampy.client import SteamClient, InvalidCredentials
from steampy.models import GameOptions, Currency



# Your Steam username
username = ''

# Path to Steamguard file
steam_guard_path = ''

# Your Steam password
password = ''

# Your Steam api key (http://steamcommunity.com/dev/apikey)
steam_key = ''


# Log in into Steam. First, we create the SteamClient object, then we log in.
print('Logging in into Steam...')
steam_client = SteamClient(steam_key)
try:
    steam_client.login(username, password, steam_guard_path)
except (ValueError, InvalidCredentials):
    print('Your login credentials are invalid!')
    exit(1)
else:
    print('Finished! Logged in into Steam')

# Get my market listings.
print('Obtaining my market listings...')
market_listings = steam_client.market.get_my_market_listings()

with open(f'get_my_market_listings.json', 'w') as file:
    json.dump(market_listings, file)

print(f'Done my market listings: get_my_market_listings.json')


# Get item orders histogram.

# 1: Mann Co. Supply Crate Key
# 20: Tour of Duty Ticket
# 176288467: Dreams & Nightmares Case

print('Obtaining item orders histogram...')
item_orders_histogram = steam_client.market.fetch_item_orders_histogram('1', Currency.EURO)

with open(f'item_orders_histogram.json', 'w') as file:
    json.dump(item_orders_histogram, file)

print(f'Done item orders histogram: item_orders_histogram.json')
