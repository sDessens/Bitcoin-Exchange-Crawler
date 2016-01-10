# Module allows query of balances from coincheck.jp


import json
import urllib
import urllib2
import time
import hashlib
import hmac
import logging

log = logging.getLogger('main.exchanges.coincheck')

from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection


def getInstance():
    return CoincheckVisitor()


class CoincheckVisitor:
    def __init__(self):
        pass

    def accept(self, json):
        try:
            return json['type'] == 'coincheck'
        except KeyError as e:
            return False

    def visit(self, json):
        api = CoincheckApi(json['pubkey'], json['privkey'])
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

        out = Collection()
        out[json['out']] = PartialBalance(btc)
        return out


class CoincheckApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)
        self.url = 'https://coincheck.jp'

    def get(self, uri):
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
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

        request = urllib2.Request(self.url + uri, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read().decode('utf-8')
        return json.loads(data)

    def query_ticker(self):
        return self.get('/api/ticker')

    def query_balance(self):
        return self.get_private('/api/accounts/balance')
