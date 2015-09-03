from unittest import TestCase

from common.conversiontable import ConversionTable, ConversionException

class TestConversionTable(TestCase):
    def test_happy(self):
        d = {
            ('LTC', 'BTC') : (0.02, 1), # 0.02 BTC = 1 LTC. cost 1
            ('XPM', 'LTC') : (0.1, 3),  # higher cost for lesser used market
            ('XPM', 'BTC') : (0.01, 2),
            ('DEV', 'LTC') : (0.1, 5),
            ('DEV', 'XPM') : (0.1, 10)
        }

        tab = ConversionTable(d)

        assert(tab.convert( 'BTC', 'BTC', 1.23 ) == 1.23)
        assert(tab.convert( 'LTC', 'BTC', 50) == 1)
        assert(tab.convert( 'BTC', 'LTC', 1) == 50)
        assert(tab.convert( 'LTC', 'BTC', 10 ) == 0.2)

        # conversion should be dev-ltc-btc, not dev-xpm-btc
        # because the cost of the latter is higher
        assert(tab.convert( 'DEV', 'BTC', 1 ) == 0.002)


    def test_unreachable(self):
        d = {
            ('LTC', 'BTC') : (0.02, 1), # 0.02 BTC = 1 LTC. cost 1
            ('XPM', 'LTC') : (0.1, 3),  # higher cost for lesser used market
            ('XPM', 'BTC') : (0.01, 2),
            ('DEV', 'FOO') : (0.1, 5),
            ('DEV', 'BAR') : (0.1, 10)
        }

        tab = ConversionTable(d)

        self.assertRaises(ConversionException, tab.convert, 'BTC', 'DEV', 10)



