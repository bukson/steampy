import os
import re
import copy
import math
import struct
from typing import List
from decimal import Decimal
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup, Tag
from requests.structures import CaseInsensitiveDict

from steampy.models import GameOptions
from steampy.exceptions import ProxyConnectionError, LoginRequired


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if not self.was_login_executed:
            raise LoginRequired('Use login method first')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def text_between(text: str, begin: str, end: str) -> str:
    start = text.index(begin) + len(begin)
    end = text.index(end, start)
    return text[start:end]


def texts_between(text: str, begin: str, end: str):
    stop = 0
    while True:
        try:
            start = text.index(begin, stop) + len(begin)
            stop = text.index(end, start)
            yield text[start:stop]
        except ValueError:
            return


def account_id_to_steam_id(account_id: str) -> str:
    first_bytes = int(account_id).to_bytes(4, byteorder='big')
    last_bytes = 0x1100001.to_bytes(4, byteorder='big')
    return str(struct.unpack('>Q', last_bytes + first_bytes)[0])


def steam_id_to_account_id(steam_id: str) -> str:
    return str(struct.unpack('>L', int(steam_id).to_bytes(8, byteorder='big')[4:])[0])


def calculate_gross_price(price_net: Decimal, publisher_fee: Decimal, steam_fee: Decimal = Decimal('0.05')) -> Decimal:
    """Calculate the price including the publisher's fee and the Steam fee.

    Arguments:
        price_net (Decimal): The amount that the seller receives after a market transaction.
        publisher_fee (Decimal): The Publisher Fee is a game specific fee that is determined and collected by the game
            publisher. Most publishers have a `10%` fee - `Decimal('0.10')` with a minimum fee of `$0.01`.
        steam_fee (Decimal): The Steam Transaction Fee is collected by Steam and is used to protect against nominal
            fraud incidents and cover the cost of development of this and future Steam economy features. The fee is
            currently `5%` (with a minimum fee of `$0.01`). This fee may be increased or decreased by Steam in the
            future.
    Returns:
        Decimal: Gross price (including fees) - the amount that the buyer pays during a market transaction
    """
    price_net *= 100
    steam_fee_amount = int(math.floor(max(price_net * steam_fee, 1)))
    publisher_fee_amount = int(math.floor(max(price_net * publisher_fee, 1)))
    price_gross = price_net + steam_fee_amount + publisher_fee_amount
    return Decimal(price_gross) / 100


def calculate_net_price(price_gross: Decimal, publisher_fee: Decimal, steam_fee: Decimal = Decimal('0.05')) -> Decimal:
    """Calculate the price without the publisher's fee and the Steam fee.

    Arguments:
        price_gross (Decimal): The amount that the buyer pays during a market transaction.
        publisher_fee (Decimal): The Publisher Fee is a game specific fee that is determined and collected by the game
            publisher. Most publishers have a `10%` fee - `Decimal('0.10')` with a minimum fee of `$0.01`.
        steam_fee (Decimal): The Steam Transaction Fee is collected by Steam and is used to protect against nominal
            fraud incidents and cover the cost of development of this and future Steam economy features. The fee is
            currently `5%` (with a minimum fee of `$0.01`). This fee may be increased or decreased by Steam in the
            future.
    Returns:
        Decimal: Net price (without fees) - the amount that the seller receives after a market transaction.
    """
    price_gross *= 100
    estimated_net_price = Decimal(int(price_gross / (steam_fee + publisher_fee + 1)))
    estimated_gross_price = calculate_gross_price(estimated_net_price / 100, publisher_fee, steam_fee) * 100

    # Since calculate_gross_price has a math.floor, we could be off a cent or two. Let's check:
    iterations = 0  # Shouldn't be needed, but included to be sure nothing unforeseen causes us to get stuck
    ever_undershot = False
    while estimated_gross_price != price_gross and iterations < 10:
        if estimated_gross_price > price_gross:
            if ever_undershot:
                break
            estimated_net_price -= 1
        else:
            ever_undershot = True
            estimated_net_price += 1

        estimated_gross_price = calculate_gross_price(estimated_net_price / 100, publisher_fee, steam_fee) * 100
        iterations += 1
    return estimated_net_price / 100


def merge_items_with_descriptions_from_inventory(inventory_response: dict, game: GameOptions) -> dict:
    inventory = inventory_response.get('assets', [])
    if not inventory:
        return {}
    descriptions = {get_description_key(description): description for description in inventory_response['descriptions']}
    return merge_items(inventory, descriptions, context_id=game.context_id)


def merge_items_with_descriptions_from_offers(offers_response: dict) -> dict:
    descriptions = {get_description_key(offer): offer for offer in offers_response['response'].get('descriptions', [])}
    received_offers = offers_response['response'].get('trade_offers_received', [])
    sent_offers = offers_response['response'].get('trade_offers_sent', [])
    offers_response['response']['trade_offers_received'] = list(
        map(lambda offer: merge_items_with_descriptions_from_offer(offer, descriptions), received_offers)
    )
    offers_response['response']['trade_offers_sent'] = list(
        map(lambda offer: merge_items_with_descriptions_from_offer(offer, descriptions), sent_offers)
    )
    return offers_response


def merge_items_with_descriptions_from_offer(offer: dict, descriptions: dict) -> dict:
    merged_items_to_give = merge_items(offer.get('items_to_give', []), descriptions)
    merged_items_to_receive = merge_items(offer.get('items_to_receive', []), descriptions)
    offer['items_to_give'] = merged_items_to_give
    offer['items_to_receive'] = merged_items_to_receive
    return offer


def merge_items_with_descriptions_from_listing(listings: dict, ids_to_assets_address: dict, descriptions: dict) -> dict:
    for listing_id, listing in listings.get('sell_listings').items():
        asset_address = ids_to_assets_address[listing_id]
        description = descriptions[asset_address[0]][asset_address[1]][asset_address[2]]
        listing['description'] = description
    return listings


def merge_items(items: List[dict], descriptions: dict, **kwargs) -> dict:
    merged_items = {}

    for item in items:
        description_key = get_description_key(item)
        description = copy.copy(descriptions[description_key])
        item_id = item.get('id') or item['assetid']
        description['contextid'] = item.get('contextid') or kwargs['context_id']
        description['id'] = item_id
        description['amount'] = item['amount']
        merged_items[item_id] = description

    return merged_items


def get_market_listings_from_html(html: str) -> dict:
    document = BeautifulSoup(html, 'html.parser')
    nodes = document.select('div[id=myListings]')[0].findAll('div', {'class': 'market_home_listing_table'})
    sell_listings_dict = {}
    buy_orders_dict = {}

    for node in nodes:
        if 'My sell listings' in node.text:
            sell_listings_dict = get_sell_listings_from_node(node)
        elif 'My listings awaiting confirmation' in node.text:
            sell_listings_awaiting_conf = get_sell_listings_from_node(node)
            for listing in sell_listings_awaiting_conf.values():
                listing['need_confirmation'] = True
            sell_listings_dict.update(sell_listings_awaiting_conf)
        elif 'My buy orders' in node.text:
            buy_orders_dict = get_buy_orders_from_node(node)

    return {'buy_orders': buy_orders_dict, 'sell_listings': sell_listings_dict}


def get_sell_listings_from_node(node: Tag) -> dict:
    sell_listings_raw = node.findAll('div', {'id': re.compile('mylisting_\d+')})
    sell_listings_dict = {}

    for listing_raw in sell_listings_raw:
        spans = listing_raw.select('span[title]')
        listing = {
            'listing_id': listing_raw.attrs['id'].replace('mylisting_', ''),
            'buyer_pay': spans[0].text.strip(),
            'you_receive': spans[1].text.strip()[1:-1],
            'created_on': listing_raw.findAll('div', {'class': 'market_listing_listed_date'})[0].text.strip(),
            'need_confirmation': False,
        }
        sell_listings_dict[listing['listing_id']] = listing

    return sell_listings_dict


def get_market_sell_listings_from_api(html: str) -> dict:
    document = BeautifulSoup(html, 'html.parser')
    sell_listings_dict = get_sell_listings_from_node(document)
    return {'sell_listings': sell_listings_dict}


def get_buy_orders_from_node(node: Tag) -> dict:
    buy_orders_raw = node.findAll('div', {'id': re.compile('mybuyorder_\\d+')})
    buy_orders_dict = {}

    for order in buy_orders_raw:
        qnt_price_raw = order.select('span[class=market_listing_price]')[0].text.split('@')
        order = {
            'order_id': order.attrs['id'].replace('mybuyorder_', ''),
            'quantity': int(qnt_price_raw[0].strip()),
            'price': qnt_price_raw[1].strip(),
            'item_name': order.a.text,
            'icon_url': order.select('img[class=market_listing_item_img]')[0].attrs['src'].rsplit('/', 2)[-2],
            'game_name': order.select('span[class=market_listing_game_name]')[0].text,
        }
        buy_orders_dict[order['order_id']] = order

    return buy_orders_dict


def get_listing_id_to_assets_address_from_html(html: str) -> dict:
    listing_id_to_assets_address = {}
    regex = "CreateItemHoverFromContainer\( [\w]+, 'mylisting_([\d]+)_[\w]+', ([\d]+), '([\d]+)', '([\d]+)', [\d]+ \);"

    for match in re.findall(regex, html):
        listing_id_to_assets_address[match[0]] = [str(match[1]), match[2], match[3]]

    return listing_id_to_assets_address


def get_description_key(item: dict) -> str:
    return f'{item["classid"]}_{item["instanceid"]}'


def get_key_value_from_url(url: str, key: str, case_sensitive: bool = True) -> str:
    params = urlparse(url).query
    return parse_qs(params)[key][0] if case_sensitive else CaseInsensitiveDict(parse_qs(params))[key][0]


def load_credentials():
    dirname = os.path.dirname(os.path.abspath(__file__))
    with open(f'{dirname}/../secrets/credentials.pwd', 'r') as f:
        return [Credentials(line.split()[0], line.split()[1], line.split()[2]) for line in f]


class Credentials:
    def __init__(self, login: str, password: str, api_key: str):
        self.login = login
        self.password = password
        self.api_key = api_key


def ping_proxy(proxies: dict):
    try:
        requests.get('https://steamcommunity.com/', proxies=proxies)
        return True
    except Exception:
        raise ProxyConnectionError('Proxy not working for steamcommunity.com')


def create_cookie(name: str, cookie: str, domain: str) -> dict:
    return {'name': name, 'value': cookie, 'domain': domain}
