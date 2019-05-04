# Module allows the retrieval of balances from binance

import urllib.request
import time
import hashlib
import hmac
import logging
import requests

from common.conversiontable import ConversionTable

log = logging.getLogger('main.exchanges.binance')


class BinanceApiException(RuntimeError):
    pass


class BinanceLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = BinanceApi(self._pubkey, self._privkey)
        return api.get_wallet_value()


class BinanceApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv
        self.url = 'https://api.binance.com'

    def _parse_response(self, json):
        if 'code' in json:
            raise BinanceApiException(json['msg'])
        return json

    def _get_auth(self, uri):
        params = {
            'recvWindow': 50 * 1000,
            'timestamp': str(int(time.time() * 1000))
        }

        post = urllib.urlencode(params)
        signature = hmac.new(self.priv, post, hashlib.sha256).hexdigest()

        headers = {
            "X-MBX-APIKEY": self.pub
        }

        url = self.url + uri + '?' + post + '&signature=' + signature
        request = requests.get(url, headers=headers)
        return self._parse_response(request.json())

    def _get(self, uri):
        url = self.url + uri
        request = requests.get(url)
        return self._parse_response(request.json())

    def get_account(self):
        return self._get_auth('/api/v3/account')

    def get_ticker(self):
        return self._get('/api/v3/ticker/price')

    def get_exchange_info(self):
        return self._get('/api/v1/exchangeInfo')

    def get_wallet_value(self):
        account = self.get_account()
        tickers = self.get_ticker()
        exchange_info = self.get_exchange_info()

        pairs = {}
        for pair in exchange_info['symbols']:
            pairs[pair['symbol']] = (pair['baseAsset'], pair['quoteAsset'])

        table = {}
        for ticker in tickers:
            quote, base = pairs[ticker['symbol']]
            table[(quote, base)] = (float(ticker['price']), 1)

        conversion_table = ConversionTable(table)

        total = 0
        for balance in account['balances']:
            asset = balance['asset']
            balance_sum = float(balance['locked']) + float(balance['free'])
            if balance_sum > 0:
                total += conversion_table.try_convert(asset, 'BTC', balance_sum)

        return total
