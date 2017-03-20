import json
import hashlib
import hmac
import urllib2
import time
import logging
from urllib import urlencode

from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.bitmarket' )


class BitmarketLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BitmarketAPI(self._pubkey, self._privkey)

        wallet = api.get_info()
        table = api.get_markets_graph()

        total = 0
        for k, v in wallet.items():
            total += table.convert(k, 'BTC', v)

        return total


class BitmarketAPI:
    MAX_MY_TRADES = 1000

    def __init__(self, pub, priv):
        self._pub = pub
        self._priv = priv
        self._url = 'https://www.bitmarket.pl'

    def _post_auth(self, method):
        url = self._url + '/api2/'

        post_data = urlencode(dict(tonce=int(time.time()),
                                   method=method))

        sign = hmac.new(self._priv, post_data, hashlib.sha512).hexdigest()
        headers = {
            'API-Key': self._pub,
            'API-Hash': sign
        }

        request = urllib2.Request(url, headers=headers, data=post_data)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def _get_public(self, uri):
        req = urllib2.Request(self._url + uri)
        return json.loads(urllib2.urlopen(req).read())

    def get_info(self):
        info = self._post_auth('info')
        result = {}
        for key, value in info['data']['balances']['available'].items() + \
                            info['data']['balances']['blocked'].items():
            amount = float(value)
            if amount:
                result[key] = amount + (result[key] if key in result else 0)
        return result

    def get_transactions(self):
        return self._post_auth('transactions')

    def get_markets(self):
        # just the subset we need
        return [(('BTC', 'PLN'), 'BTCPLN')]

    def get_ticker_price(self, pair):
        ticker = self._get_public('/json/{pair}/ticker.json'.format(pair=pair))
        return (float(ticker['bid']) + float(ticker['ask'])) / 2

    def get_markets_graph(self):
        result = {}
        for pair, market in self.get_markets():
            result[pair] = (self.get_ticker_price(market), 1)
        return ConversionTable(result)

