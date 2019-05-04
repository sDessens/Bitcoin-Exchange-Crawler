# Module allows query of recent bitcoin prices from bitcoinaverage api

import json
import urllib.request, urllib.error, urllib.parse
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
    def __init__(self, currency = "BTC"):
        self.url = 'https://apiv2.bitcoinaverage.com'
        self._currency = currency

    def get(self, uri):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib.request.Request(self.url + uri, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_ticker(self, currency):
        return self.get('/ticker/%s' % currency)

    def query_fiat(self):
        uri = "/indices/global/ticker/short?crypto={}&fiat=USD,EUR".format(self._currency)
        result = self.get(uri)
        rates = {}
        if result != {}:
            eur = "{}EUR".format(self._currency)
            usd = "{}USD".format(self._currency)
            rates[eur] = result[eur]["last"]
            rates[usd] = result[usd]["last"]
            rates["EURUSD"] = rates[eur] / rates[usd]
        return rates
