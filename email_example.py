from json import dump
from steampy.client import SteamClient, InvalidCredentials
from steampy.models import GameOptions

steamAuthCodes = {}

def emailCallback() -> str:
    return input("Code is required for authentication!")

def saveCallback(response) -> None:
    key = response['steamid']

    try:
        value = response['webcookie']
    except KeyError:
        return

    with open('cookies.txt', 'a') as f:
        f.write('{}:{}'.format(key, value))
        
def loadAuthCodes() -> dict:
    with open('cookies.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            key, value = line.split(':')
            steamAuthCodes['steamMachineAuth' + key] = value


#Your steam username
username = ''

#Path to steam guard file
steam_guard_path = ''

#Your steam password
password = ''

#Your steam api key (http://steamcommunity.com/dev/apikey)
steam_key = ''

loadAuthCodes()
#Log into steam. First, we create the SteamClient object, then we login
print("Logging into steam")
steam_client = SteamClient(steam_key)
try:
    steam_client.login(username, password, emailCallback, saveCallback, steamAuthCodes)
except TypeError as e:
    print(e)
    exit(1)
print("Finished! Logged into steam")

steam_client.logout()
