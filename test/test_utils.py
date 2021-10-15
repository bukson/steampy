import decimal
from unittest import TestCase

from steampy import utils


class TestUtils(TestCase):

    def test_text_between(self):
        text = 'var a = "dupadupa";'
        text_between = utils.text_between(text, 'var a = "', '";')
        self.assertEqual(text_between, 'dupadupa')
        
    def test_texts_between(self):
        text = "<li>element 1</li>\n<li>some random element</li>"
        items = []
        for el in utils.texts_between(text, "<li>", "</li>"):
            items.append(el)
        self.assertEqual(items, ["element 1", "some random element"])

    def test_account_id_to_steam_id(self):
        account_id = '358617487'
        steam_id = utils.account_id_to_steam_id(account_id)
        self.assertEqual('76561198318883215', steam_id)

    def test_steam_id_to_account_id(self):
        steam_id = '76561198318883215'
        account_id = utils.steam_id_to_account_id(steam_id)
        self.assertEqual(account_id, '358617487')

    def test_parse_price_with_currency_symbol(self):
        price = '$11.33 USD'
        decimal_price = utils.parse_price(price)
        self.assertEqual(decimal_price, decimal.Decimal('11.33'))

    def test_parse_price_without_currency_symbol(self):
        price = '11,33 USD'
        decimal_price = utils.parse_price(price)
        self.assertEqual(decimal_price, decimal.Decimal('11.33'))

    def test_parse_price_without_space(self):
        price = '21,37zł'
        decimal_price = utils.parse_price(price)
        self.assertEqual(decimal_price, decimal.Decimal('21.37'))

    def test_parse_price_without_decimal_separator(self):
        price = '2137 CZK'
        decimal_price = utils.parse_price(price)
        self.assertEqual(decimal_price, decimal.Decimal('2137'))

    def test_get_key_value_from_url(self):
        url = 'https://steamcommunity.com/tradeoffer/new/?partner=aaa&token=bbb'
        self.assertEqual(utils.get_key_value_from_url(url, 'partner'), 'aaa')
        self.assertEqual(utils.get_key_value_from_url(url, 'token'), 'bbb')

    def test_get_key_value_from_url_case_insensitive(self):
        url = 'https://steamcommunity.com/tradeoffer/new/?Partner=aaa&Token=bbb'
        self.assertEqual(utils.get_key_value_from_url(url, 'partner', case_sensitive=False), 'aaa')
        self.assertEqual(utils.get_key_value_from_url(url, 'token', case_sensitive=False), 'bbb')