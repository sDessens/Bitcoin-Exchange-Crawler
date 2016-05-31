# Module allows query of recent bitcoin prices from bitcoinaverage api

import json
import urllib2
import logging

log = logging.getLogger('main.exchanges.bitcoinaverage')


class BitcoinAverageLastBalance:
    def __init__(self, currency):
        self._currency = currency

    def crawl(self):
        api = BitcoinAverageApi()
        ticker = api.query_ticker(self._currency)
        price = ticker['last']
        return price


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
