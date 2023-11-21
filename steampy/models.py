"""
Provides models to interact with Steam API
"""
from enum import IntEnum
from collections import namedtuple


class GameOptions:
    PredefinedOptions = namedtuple('PredefinedOptions', ['app_id', 'context_id'])

    STEAM = PredefinedOptions('753', '6')
    DOTA2 = PredefinedOptions('570', '2')
    CS = PredefinedOptions('730', '2')
    TF2 = PredefinedOptions('440', '2')
    PUBG = PredefinedOptions('578080', '2')
    RUST = PredefinedOptions('252490', '2')

    def __init__(self, app_id: str, context_id: str) -> None:
        self.app_id = app_id
        self.context_id = context_id


class Asset:
    def __init__(self, asset_id: str, game: GameOptions, amount: int = 1) -> None:
        self.asset_id = asset_id
        self.game = game
        self.amount = amount

    def to_dict(self) -> dict:
        return {
            'appid': int(self.game.app_id),
            'contextid': self.game.context_id,
            'amount': self.amount,
            'assetid': self.asset_id,
        }


class Currency(IntEnum):
    """
    All currencies that are supported by Steam you can found them at https://partner.steamgames.com/doc/store/pricing/currencies
    """
    USD = 1
    """United States Dollar"""
    GBP = 2
    """United Kingdom Pound"""
    EURO = 3
    """European Union Euro"""
    CHF = 4
    """Swiss Francs"""
    RUB = 5
    """Russian Rouble"""
    PLN = 6
    """Polish Złoty"""
    BRL = 7
    """Brazilian Reals"""
    JPY = 8
    """Japanese Yen"""
    NOK = 9
    """Norwegian Krone"""
    IDR = 10
    """Indonesian Rupiah"""
    MYR = 11
    """Malaysian Ringgit"""
    PHP = 12
    """Philippine Peso"""
    SGD = 13
    """Singapore Dollar"""
    THB = 14
    """Thai Baht"""
    VND = 15
    """Vietnamese Dong"""
    KRW = 16
    """South Korean Won"""
    TRY = 17
    """	Turkish Lira"""
    UAH = 18
    """Ukrainian Hryvnia"""
    MXN = 19
    """Mexican Peso"""
    CAD = 20
    """Canadian Dollars"""
    AUD = 21
    """Australian Dollars"""
    NZD = 22
    """New Zealand Dollar"""
    CNY = 23
    """Chinese Renminbi (yuan)"""
    INR = 24
    """Indian Rupee"""
    CLP = 25
    """Chilean Peso"""
    PEN = 26
    """Peruvian Sol"""
    COP = 27
    """Colombian Peso"""
    ZAR = 28
    """South African Rand"""
    HKD = 29
    """Hong Kong Dollar"""
    TWD = 30
    """New Taiwan Dollar"""
    SAR = 31
    """Saudi Riyal"""
    AED = 32
    """United Arab Emirates Dirham"""
    SEK = 33
    """Swedish Krona"""
    ARS = 34
    """Argentine Peso"""
    ILS = 35
    """Israeli New Shekel"""
    BYN = 36
    """Belarusian Ruble"""
    KZT = 37
    """Kazakhstani Tenge"""
    KWD = 38
    """Kuwaiti Dinar"""
    QAR = 39
    """Qatari Riyal"""
    CRC = 40
    """Costa Rican Colón"""
    UYU = 41
    """Uruguayan Peso"""
    BGN = 42
    """Bulgarian Lev"""
    HRK = 43
    """Croatian Kuna"""
    CZK = 44
    """Czech Koruna"""
    DKK = 45
    """Danish Krone"""
    HUF = 46
    """Hungarian Forint"""
    RON = 47
    """Romanian Leu"""


class TradeOfferState(IntEnum):
    """These are the different states for a trade offer. More information at https://developer.valvesoftware.com/wiki/Steam_Web_API/IEconService#ETradeOfferState"""
    Invalid = 1
    """Invalid"""
    Active = 2
    """This trade offer has been sent, neither party has acted on it yet."""
    Accepted = 3
    """The trade offer was accepted by the recipient and items were exchanged."""
    Countered = 4
    """The recipient made a counter offer."""
    Expired = 5
    """The trade offer was not accepted before the expiration date."""
    Canceled = 6
    """The sender cancelled the offer."""
    Declined = 7
    """The recipient declined the offer."""
    InvalidItems = 8
    """Some of the items in the offer are no longer available (indicated by the missing flag in the output)."""
    ConfirmationNeed = 9
    """The offer hasn't been sent yet and is awaiting email/mobile confirmation. The offer is only visible to the sender."""
    CanceledBySecondaryFactor = 10
    """Either party canceled the offer via email/mobile. The offer is visible to both parties, even if the sender canceled it before it was sent."""
    StateInEscrow = 11
    """The trade has been placed on hold. The items involved in the trade have all been removed from both parties' inventories and will be automatically delivered in the future."""


class SteamUrl:
    API_URL = 'https://api.steampowered.com'
    COMMUNITY_URL = 'https://steamcommunity.com'
    STORE_URL = 'https://store.steampowered.com'
    LOGIN_URL = 'https://login.steampowered.com'


class Endpoints:
    CHAT_LOGIN = f'{SteamUrl.API_URL}/ISteamWebUserPresenceOAuth/Logon/v1'
    SEND_MESSAGE = f'{SteamUrl.API_URL}/ISteamWebUserPresenceOAuth/Message/v1'
    CHAT_LOGOUT = f'{SteamUrl.API_URL}/ISteamWebUserPresenceOAuth/Logoff/v1'
    CHAT_POLL = f'{SteamUrl.API_URL}/ISteamWebUserPresenceOAuth/Poll/v1'
