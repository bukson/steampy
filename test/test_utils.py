from unittest import TestCase

from steampy import utils


class TestGuard(TestCase):

    def test_text_between(self):
        text = 'var a = "dupadupa";'
        text_between = utils.text_between(text, 'var a = "', '";')
        self.assertEquals(text_between, 'dupadupa')

    def test_account_id_to_steam_id(self):
        account_id = '358617487'
        steam_id = utils.account_id_to_steam_id(account_id)
        self.assertEquals('76561198318883215', steam_id)

    def test_steam_id_to_account_id(self):
        steam_id = '76561198318883215'
        account_id = utils.steam_id_to_account_id(steam_id)
        self.assertEquals(account_id, '358617487')

    def test_price_to_float(self):
        price = '$11.33 USD'
        float_price = utils.price_to_float(price)
        self.assertEquals(float_price, 11.33)
