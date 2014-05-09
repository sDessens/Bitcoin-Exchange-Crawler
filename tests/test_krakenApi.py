from unittest import TestCase

__author__ = 'Stefan'

import read.kraken
import json
import logging

class TestKrakenApi(TestCase):
    def test__parseResponse(self):
        FORMAT = "%(asctime)-15s %(levelname)s %(name)s: %(message)s"
        logging.basicConfig(format=FORMAT)


        response = '{"error":[],"result":{"tb":"0.4574076281","m":"0.0000000000","n":"0.0000000000","c":"0.0000000000","v":"0.0000000000","e":"0.4574076281","mf":"0.4574076281"}}'
        errorResponse = '{"error":["EAPI:Invalid key"]}'

        api = read.kraken.KrakenApi(
            'bogus-public-key',
            '5555555555555555555555555555555555555555555555555555555555555555555555555555555555555Q==' )

        self.assertAlmostEqual( api._parseResponse( json.loads(response) ),
                                0.4574076281, 5 )

        try:
            api._parseResponse( json.loads(errorResponse) )
            self.fail( 'exception should be thrown' )
        except Exception as e:
            pass