from unittest import TestCase

__author__ = 'Stefan'

import readdb.blockchain as blockchain
import common.balanceData as balanceData
from dateutil import parser
import logging


class TestBlockchainReadAddressIntoBalanceData(TestCase):
    def test_parse(self):
        FORMAT = "%(asctime)-15s %(levelname)s %(name)s: %(message)s"
        logging.basicConfig(format=FORMAT)


        bc = blockchain.BlockchainReadAddressIntoBalanceData()

        bd = bc.parse( '1HWu9y8WbryyEiX1aUzw5vtDmQWn7jVkf2' )

        self.assertIsInstance( bd, balanceData.BalanceData )
        self.assertAlmostEqual( bd.interpolate( parser.parse("Aug 28 1999 12:00") ), 0, 3)
        self.assertAlmostEqual( bd.interpolate( parser.parse("Mar 10 2014 12:00") ), 0.7494, 3 )
        self.assertAlmostEqual( bd.interpolate( parser.parse("Apr 18 2014 12:00") ), 1.9994, 3 )





