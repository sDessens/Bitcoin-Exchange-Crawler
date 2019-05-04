# Module allows the retrieval of balances from Cex.io

import json
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error
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
            if v:
                total += table.try_convert(k, 'BTC', v)
        return total

    def crawl_trades(self):
        api = CexApi(self._pubkey, self._privkey, self._username)
        trades = {}
        for pair in ['BTC/USD', 'ETH/BTC', 'ETH/USD','BTC/EUR','ETH/EUR']:
            for retries in range(10):
                try:
                    new_trades = api.archived_orders(pair)
                    if 'error' in new_trades:
                        print(new_trades)
                        continue  # retry
                    trades[pair] = new_trades
                except urllib.error.HTTPError as e:
                    print('timeout... retying', pair)
                    continue
                break
        return trades

    def crawl_balance(self):
        api = CexApi(self._pubkey, self._privkey, self._username)
        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in list(wallet.items()):
            if not k in ["LTC","BTG","GHS","XRP","BSV","OMG"]:
                total += table.convert(k, 'BTC', v)
        wallet["Total_BTC"] = total
        return wallet

class CexApi:
    def __init__(self, pub, priv, username):
        self.pub = str(pub)
        self.priv = priv.encode("utf-8")
        self.user = str(username)

    def _get(self, www, uri, params):
        params['nonce'] = str(int(time.time()*1000000))
        params['key'] = self.pub
        plain_text = params['nonce'] + self.user + self.pub
        params['signature'] = hmac.new(self.priv, plain_text.encode("utf-8"), hashlib.sha256).hexdigest()

        req = urllib.request.Request(www + uri, urllib.parse.urlencode(params).encode("utf-8"))
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib.request.urlopen(req).read())

    def _get_public(self, www, uri):
        req = urllib.request.Request(www + uri)
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib.request.urlopen(req).read())

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
        print(js)
        return js

    def getWallet(self):
        www = 'https://cex.io'
        uri = '/api/balance/'

        js = self._get(www, uri, {})
        if 'error' in js:
            raise Exception(js['error'])

        wallet = {}

        for k, v in list(js.items()):
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
            if not 'bid' in js or not 'ask' in js:
                continue
            try:
                bid = float(js['bid'])
                ask = float(js['ask'])
                avg = (bid + ask) / 2
                diff = abs(bid - ask) / avg
            except:
                avg = float(js['last'])
                diff = 0.0
            graph[(pri, sec)] = (avg, diff)

        return graph
