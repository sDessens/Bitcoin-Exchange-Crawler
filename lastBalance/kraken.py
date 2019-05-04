# Module allows the retrieval of balances from Kraken

import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import time
import hashlib
import hmac
import base64
import logging

log = logging.getLogger( 'main.exchanges.kraken' )


class KrakenLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = KrakenApi(self._pubkey, self._privkey)
        return api.getBalance('BTC')

    def crawl_trades(self):
        api = KrakenApi(self._pubkey, self._privkey)
        js = api.getTradeHistory()
        return js['trades']

    def crawl_balance(self):
        api = KrakenApi(self._pubkey, self._privkey)
        mapping = api.getKeyAltnamesMapping()
        balance = api.getWalletBalance()
        mappedbalance = {}
        for key, bal in balance.items():
            if key.upper() == 'XXBT':
                mappedbalance['BTC'] = float(bal)
            else:
                mappedbalance[mapping[key]] = float(bal)
        mappedbalance["Total_BTC"] = api.getBalance('BTC')
        return mappedbalance


class KrakenApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv

    def getBalance(self, key):
        key = { 'BTC' : 'XXBT',
                'EUR' : 'ZEUR',
                'USD' : 'ZUSD'}[key.upper()]

        json = self._query_private( 'TradeBalance', { 'asset' : key } )
        return self._parseResponse(json)

    def getOrderBalance(self):
        balance = {}
        json = self._query_private('OpenOrders', {})
        for key, order in json['result']['open'].items():
            vol = float(order['vol'])
            price = float(order['descr']['price'])
            if order['descr']['type'] == "sell":
                balance[order['descr']['pair']] = vol
            else:
                balance[order['descr']['pair']] = vol*price
        return balance
    def getKeyAltnamesMapping(self):
        json = self._query('/0/public/Assets', {})
        keys = {}
        for key, decription in json['result'].items():
            keys[key] = decription["altname"]
        return keys

    def getWalletBalance(self):
        json = self._query_private( 'Balance', { } )
        return json['result']

    def getTradeHistory(self):
        json = self._query_private('TradesHistory', {})
        return json['result']

    def _parseResponse(self, json):
        if 'result' in json:
            return float(json['result']['eb'])
        else:
            log.error( '{0}'.format( str( json['error']) ) )
            raise Exception()

    def _query(self, path, params, headers = {}):
        url = 'https://api.kraken.com' + path
        post = urllib.parse.urlencode( params ).encode("utf-8")
        headers['user-agent'] = 'bot'
        ret = urllib.request.urlopen(urllib.request.Request( url, post, headers ))
        return json.loads(ret.read())

    def _query_public(self, method, params):
        return self._query( '/0/public/' + method, params )

    def _query_private(self, method, params):
        url = 'https://api.kraken.com/'
        path = '/0/private/' + method

        params['nonce'] = int(time.time()*1000)
        postdata = urllib.parse.urlencode(params)

        # Unicode-objects must be encoded before hashing
        encoded = (str(params['nonce']) + postdata).encode()
        message = path.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.priv),
                             message, hashlib.sha512)
        headers = {
            'API-Key': self.pub,
            'API-Sign': base64.b64encode(signature.digest())
        }

        return self._query( path, params, headers )

if __name__ == '__main__':
    api = KrakenLastBalance('S5fGxCsAkASnNMJ10+7W/k32GlJImi92RVL2Ttt7K9cyS7Y8YYsW7HSA',
                      'kAKroFx3cayY+Vki+mgd5SYnRaTcwQme5+YhkD5yixn/r8xd/igtn2u5lUZ83vdtmXT2d71gMR0ASTe/uj0OlA==')
    print(api.crawl_balance())