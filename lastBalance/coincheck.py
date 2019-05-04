# Module allows query of balances from coincheck.jp

import json
import urllib.request, urllib.error, urllib.parse
import time
import hashlib
import hmac
import logging

log = logging.getLogger('main.exchanges.coincheck')


class CoincheckLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = CoincheckApi(self._pubkey, self._privkey)
        ticker = api.query_ticker()
        jpy_price = float(ticker['last'])
        funds = api.query_balance()
        btc = (+ float(funds['btc'])
               + float(funds['btc_reserved'])
               + float(funds['btc_lend_in_use'])
               - float(funds['btc_lent'])
               - float(funds['btc_debt'])
               + float(funds['jpy_reserved']) / jpy_price
               + float(funds['jpy']) / jpy_price
               + float(funds['jpy_lend_in_use']) / jpy_price
               - float(funds['jpy_lent']) / jpy_price
               - float(funds['jpy_debt']) / jpy_price
               )

        return btc

class CoincheckApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)
        self.url = 'https://coincheck.jp'

    def get(self, uri):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib.request.Request(self.url + uri, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def get_private(self, uri):
        nonce = str(int(time.time() * 1000000)) # us
        url = self.url + uri
        body = ""

        message = nonce + url+ body
        headers = {
            "ACCESS-KEY" : self.pub,
            "ACCESS-NONCE": nonce,
            "ACCESS-SIGNATURE": hmac.new(self.priv, message, hashlib.sha256).hexdigest().lower()
        }

        request = urllib.request.Request(self.url + uri, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_ticker(self):
        return self.get('/api/ticker')

    def query_balance(self):
        return self.get_private('/api/accounts/balance')
