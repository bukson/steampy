import json

from steampy.client import SteamClient, InvalidCredentials
from steampy.models import GameOptions


# Your Steam username
username = ''

# Path to Steamguard file
steam_guard_path = ''

# Your Steam password
password = ''

# Your Steam api key (http://steamcommunity.com/dev/apikey)
steam_key = ''

# The game's app id. If not supplied, it will ask for input later
app_id = ''

# The game's context id. If not supplied, it will ask for input later
context_id = ''


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


# We'll ask them for the game's app id and context id of the inventory
if not app_id:
    app_id = input('What is the app id?\n')
if not context_id:
    context_id = input("What is the context id of that game's inventory? (usually 2)\n")


# Get all the items in the inventory. Save name and amount for each item.
print('Obtaining inventory...')
item_amounts = {}
inventory = steam_client.get_my_inventory(GameOptions(app_id, context_id))
for item in inventory.values():
    if item['market_name'] in item_amounts:
        item_amounts[item['market_name']] += 1
    else:
        item_amounts[item['market_name']] = 1
print(f'Done obtaining inventory for the game: {app_id}')


# Dump all the info to inventory_(app_id)_(context_id).json file
print('Saving information...')
with open(f'inventory_{app_id}_{context_id}.json', 'w') as file:
    json.dump(item_amounts, file)
print(f'Done! Saved to file: inventory_{app_id}_{context_id}.json')
