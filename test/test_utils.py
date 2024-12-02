from decimal import Decimal
from unittest import TestCase

from steampy import utils


class TestUtils(TestCase):
    def test_text_between(self) -> None:
        text = 'var a = "dupadupa";'
        text_between = utils.text_between(text, 'var a = "', '";')
        assert text_between == 'dupadupa'

    def test_texts_between(self) -> None:
        text = '<li>element 1</li>\n<li>some random element</li>'
        items = list(utils.texts_between(text, '<li>', '</li>'))
        assert items == ['element 1', 'some random element']

    def test_account_id_to_steam_id(self) -> None:
        account_id = '358617487'
        steam_id = utils.account_id_to_steam_id(account_id)
        assert steam_id == '76561198318883215'

    def test_steam_id_to_account_id(self) -> None:
        steam_id = '76561198318883215'
        account_id = utils.steam_id_to_account_id(steam_id)
        assert account_id == '358617487'

    def test_get_key_value_from_url(self) -> None:
        url = 'https://steamcommunity.com/tradeoffer/new/?partner=aaa&token=bbb'
        assert utils.get_key_value_from_url(url, 'partner') == 'aaa'
        assert utils.get_key_value_from_url(url, 'token') == 'bbb'

    def test_get_key_value_from_url_case_insensitive(self) -> None:
        url = 'https://steamcommunity.com/tradeoffer/new/?Partner=aaa&Token=bbb'
        assert utils.get_key_value_from_url(url, 'partner', case_sensitive=False) == 'aaa'
        assert utils.get_key_value_from_url(url, 'token', case_sensitive=False) == 'bbb'

    def test_calculate_gross_price(self) -> None:
        steam_fee = Decimal('0.05')  # 5%
        publisher_fee = Decimal('0.1')  # 10%

        assert utils.calculate_gross_price(Decimal('0.01'), publisher_fee, steam_fee) == Decimal('0.03')
        assert utils.calculate_gross_price(Decimal('0.10'), publisher_fee, steam_fee) == Decimal('0.12')
        assert utils.calculate_gross_price(Decimal(100), publisher_fee, steam_fee) == Decimal(115)

    def test_calculate_net_price(self) -> None:
        steam_fee = Decimal('0.05')  # 5%
        publisher_fee = Decimal('0.1')  # 10%

        assert utils.calculate_net_price(Decimal('0.03'), publisher_fee, steam_fee) == Decimal('0.01')
        assert utils.calculate_net_price(Decimal('0.12'), publisher_fee, steam_fee) == Decimal('0.10')
        assert utils.calculate_net_price(Decimal(115), publisher_fee, steam_fee) == Decimal(100)
