from json import dump
from steampy.client import SteamClient, InvalidCredentials
from steampy.models import GameOptions

#Your steam username
username = ''

#Path to steam guard file
steam_guard_path = ''

#Your steam password
password = ''

#Your steam api key (http://steamcommunity.com/dev/apikey)
steam_key = ''

#The game's app id. If not supplied, it will ask for input later
app_id = ''

#The game's context id. If not supplied, it will ask for input later
context_id = ''

#Log into steam. First, we create the SteamClient object, then we login
print("Logging into steam")
steam_client = SteamClient(steam_key)
try:
    steam_client.login(username, password, steam_guard_path)
except (ValueError, InvalidCredentials):
    print('Your login credentials are invalid')
    exit(1)
print("Finished! Logged into steam")

#we will ask them for the game's app id and context id of the inventory
if not app_id:
    app_id = input('What is the app id?\n')
if not context_id:
    context_id = input('What is the context id of that game\'s inventory? (usually 2)\n')

#get all the items in inventory, and save each name of item and the amount
print('Obtaining inventory...')
item_amounts = {}
inventory = steam_client.get_my_inventory(GameOptions(app_id,context_id))
for item in inventory.values():
    if item["market_name"] in item_amounts:
        item_amounts[item['market_name']] += 1
    else:
        item_amounts[item['market_name']] = 1
print('Done reading inventory for game: {}'.format(app_id))

#dump all the information into inventory_(app_id)_(context_id).json file
print('Saving information....')
with open('inventory_{0}_{1}.json'.format(app_id, context_id), 'w') as file:
    dump(item_amounts, file)
print('Done! Saved to file: inventory_{0}_{1}.json'.format(app_id, context_id))
