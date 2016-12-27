# Module allows the retrieval of balances from Cex.io

import json
import urllib2
import urllib
import time
import hashlib
import hmac
import logging
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.cex' )

class CexLastBalance:
    def __init__(self, pubkey, privkey, username):
        self._pubkey = pubkey
        self._privkey = privkey
        self._username = username

    def crawl(self):
        api = CexApi(self._pubkey, self._privkey, self._username)

        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in wallet.items():
            total += table.convert(k, 'BTC', v)
        return total

    def crawl_trades(self):
        api = CexApi(self._pubkey, self._privkey, self._username)
        trades = {}
        for pair in ['BTC/USD', 'ETH/BTC', 'ETH/USD']:
            for retries in range(10):
                try:
                    trades[pair] = api.archived_orders(pair)
                except urllib2.HTTPError as e:
                    print 'timeout... retying', pair
                    continue
                break
        return trades

class CexApi:
    def __init__(self, pub, priv, username):
        self.pub = str(pub)
        self.priv = str(priv)
        self.user = str(username)

    def _get(self, www, uri, params):
        params['nonce'] = str(int(time.time()*1000000))
        params['key'] = self.pub
        params['signature'] = hmac.new(self.priv, params['nonce'] + self.user + self.pub, hashlib.sha256).hexdigest()

        req = urllib2.Request(www + uri, urllib.urlencode(params))
        print urllib.urlencode(params)
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib2.urlopen(req).read())

    def _get_public(self, www, uri):
        req = urllib2.Request(www + uri)
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib2.urlopen(req).read())

    def archived_orders(self, pair):
        params = {
            'limit': 2000,
            # these arguments are documented to do something sensible, but do nothing:
            # 'dateFrom' : ts_from,
            # 'dateTo': ts_from + 2,
            # 'lastTxDateFrom' : ts_from,
            # 'lastTxDateTo': ts_from + 60*60*24*7,
            'status': 'cd'
        }
        js = self._get('https://cex.io', '/api/archived_orders/' + pair, params)
        return js

    def getWallet(self):
        www = 'https://cex.io'
        uri = '/api/balance/'

        js = self._get(www, uri, {})
        if 'error' in js:
            raise Exception(js['error'])

        wallet = {}

        for k, v in js.items():
            if len(k) == 3:
                wallet[k] = float(v["available"]) 
                if "orders" in v:
                    wallet[k] += float(v["orders"])

        return wallet

    def getMarkets(self):
        js = self._get('https://cex.io', '/api/currency_limits', {})

        symbols = []
        for p in js['data']["pairs"]:
            symbols.append((p['symbol1'], p['symbol2']))
        return symbols

    def getMarketsGraph(self):
        graph = {}
        www = 'https://cex.io'
        for pri, sec in self.getMarkets():
            uri = '/api/ticker/%s/%s' % (pri, sec)
            js = self._get(www, uri, {})
            if 'error' in js:
                continue
            bid = float(js['bid'])
            ask = float(js['ask'])
            avg = (bid + ask) / 2
            diff = abs(bid - ask) / avg
            graph[(pri, sec)] = (avg, diff)

        return graph
