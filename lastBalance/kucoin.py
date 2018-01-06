# Module allows the retrieval of balances from kucoin
import base64
import urllib
import time
import hashlib
import hmac
import logging
import requests

from common.conversiontable import ConversionTable

log = logging.getLogger('main.exchanges.kucoin')


class KucoinApiException(RuntimeError):
    pass


class KucoinLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = KucoinApi(self._pubkey, self._privkey)
        return api.get_wallet_value()


class KucoinApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv
        self.url = 'https://api.kucoin.com'

    def _parse_response(self, json):
        if json['code'] != 'OK':
            raise KucoinApiException(json['msg'])
        return json['data']

    def _get_auth(self, uri):
        body = ''
        nonce = str(int(time.time() * 1000))

        message = uri + '/' + nonce + '/' + body
        signature = hmac.new(self.priv, base64.b64encode(message), hashlib.sha256).hexdigest()

        headers = {
                "KC-API-KEY": self.pub,
                "KC-API-NONCE": nonce,
                "KC-API-SIGNATURE": signature
        }

        request = requests.get(self.url + uri, headers=headers)
        return self._parse_response(request.json())

    def _get(self, uri):
        url = self.url + uri
        request = requests.get(url)
        return self._parse_response(request.json())

    def get_balance(self):
        return self._get_auth('/v1/account/balance')

    def get_symbols(self):
        return self._get('/v1/market/open/symbols')

    def get_wallet_value(self):
        balances = self.get_balance()
        symbols = self.get_symbols()

        table = {}
        for ticker in symbols:
            quote, base = ticker['coinType'], ticker['coinTypePair']
            table[(quote, base)] = ((ticker['buy'] + ticker['sell']) / 2, float(ticker['volValue']))

        conversion_table = ConversionTable(table)

        total = 0
        for balance in balances:
            amount = balance['balance'] + balance['freezeBalance']
            if amount > 0:
                value = conversion_table.try_convert(
                    balance['coinType'], 'BTC', amount)
                total += value
        return total
