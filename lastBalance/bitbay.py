import json
import hashlib
import hmac
import urllib.request, urllib.error, urllib.parse
import time
import logging
from urllib.parse import urlencode

from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.bitbay' )


class BitbayLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BitbayAPI(self._pubkey, self._privkey)

        wallet = api.get_info()
        table = api.get_markets_graph()

        total = 0
        for k, v in list(wallet.items()):
            total += table.convert(k, 'BTC', v)

        return total


class BitbayAPI:
    MAX_MY_TRADES = 1000

    def __init__(self, pub, priv):
        self._pub = pub
        self._priv = priv
        self._url = 'https://bitbay.net'

    def _post_auth(self, method):
        url = self._url + '/API/Trading/tradingApi.php'

        post_data = urlencode(dict(moment=int(time.time()),
                                   method=method))

        sign = hmac.new(self._priv, post_data, hashlib.sha512).hexdigest()
        headers = {
            'API-Key': self._pub,
            'API-Hash': sign
        }

        request = urllib.request.Request(url, headers=headers, data=post_data)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def _get_public(self, uri):
        req = urllib.request.Request(self._url + uri)
        return json.loads(urllib.request.urlopen(req).read())

    def get_info(self):
        info = self._post_auth('info')
        result = {}
        for key, details in list(info['balances'].items()):
            value = float(details['available']) + float(details['locked'])
            if value:
                result[key] = value
        return result

    def get_transactions(self):
        return self._post_auth('transactions')

    def get_markets(self):
        # just the subset we need
        return [(('BTC', 'PLN'), 'BTCPLN'), (('BTC', 'USD'), 'BTCUSD')]

    def get_ticker_price(self, pair):
        ticker = self._get_public('/API/Public/{pair}/ticker.json'.format(pair=pair))
        return (float(ticker['bid']) + float(ticker['ask'])) / 2

    def get_markets_graph(self):
        result = {}
        for pair, market in self.get_markets():
            result[pair] = (self.get_ticker_price(market), 1)
        return ConversionTable(result)

