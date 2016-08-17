import enum
import struct

class GameOptions(enum.Enum):
    DOTA2 = ('570', '2')
    CS = ('730', '2')

    def __init__(self, app_id: str, context_id: str) -> None:
        self.app_id = app_id
        self.context_id = context_id


def text_between(text: str, begin: str, end: str) -> str:
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]


def account_id_to_steam_id(account_id: str) -> str:
    first_bytes = int(account_id).to_bytes(4, byteorder='big')
    last_bytes = 0x1100001.to_bytes(4, byteorder='big')
    return str(struct.unpack('>Q', last_bytes + first_bytes)[0])


def steam_id_to_account_id(steam_id: str) -> str:
    return str(struct.unpack('>L', int(steam_id).to_bytes(8, byteorder='big')[4:])[0])


def merge_items_with_descriptions(inventory_response: dict, game: GameOptions) -> dict:
    rg_inventory = inventory_response['rgInventory']
    rg_descriptions = inventory_response['rgDescriptions']
    merged_items = {}
    for item_id, item in rg_inventory.items():
        description_key = item['classid'] + '_' + item.get('instanceid')
        description = rg_descriptions[description_key]
        description['contextid'] = game.context_id
        description['id'] = item_id
        description['amount'] = item['amount']
        merged_items[item_id] = description
    return merged_items
