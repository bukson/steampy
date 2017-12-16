import time
from steampy.client import SteamClient
from steampy.chat import SteamChat  # works on the root of the project

# Set API key
api_key = ''
# Set path to SteamGuard file
steamguard_path = ''
# Steam username
username = ''
# Steam password
password = ''


def main():
    print('This is the chat bot.')
    if not are_credentials_filled():
        print('You have to fill the credentials to run the example')
        print('Terminating bot')
        return
    client = SteamClient(api_key)
    client.login(username, password, steamguard_path)
    chat = SteamChat(client._session)
    chat.chat_login()
    print('Bot logged in successfully, polling messages every 10 seconds')
    while True:
        time.sleep(10)
        messages = chat.chat_poll()
        for message in messages:
            print("Got message from", message.get("from"), ": ", message.get("message"))


def are_credentials_filled() -> bool:
    return api_key != '' and steamguard_path != '' and username != '' and password != ''


if __name__ == "__main__":
    # execute only if run as a script
    main()
