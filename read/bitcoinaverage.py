# Module allows query of recent bitcoin prices from bitcoinacerage


import json
import urllib
import urllib2
import time
import hashlib
import hmac
import logging

log = logging.getLogger('main.exchanges.bitcoinaverage')

from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection


def getInstance():
    return BitcoinAverageVisitor()


class BitcoinAverageVisitor:
    def __init__(self):
        pass

    def accept(self, json):
        try:
            return json['type'] == 'bitcoinaverage'
        except KeyError as e:
            return False

    def visit(self, json):
        api = BitcoinAverageApi()
        ticker = api.query_ticker(json['currency'])
        price = ticker['last']

        out = Collection()
        out[json['out']] = PartialBalance(price)
        return out


class BitcoinAverageApi:
    def __init__(self):
        self.url = 'https://api.bitcoinaverage.com'

    def get(self, uri):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_ticker(self, currency):
        return self.get('/ticker/%s' % currency)
