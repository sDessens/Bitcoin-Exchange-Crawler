# Module allows the retrieval of balances from Cex.io

import json
import urllib2
import urllib
import time
import hashlib
import hmac
import logging
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.cex' )

def getInstance():
    return CexVisitor()

class CexVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'cex'
        except Exception as e:
            return False

    def visit( self, json ):
        api = CexApi( json['pubkey'], json['privkey'], json['username'] )
        out = Collection()

        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in wallet.items():
            total += table.convert(k, 'BTC', v)
        out[json['out']] = PartialBalance( total )
        return out

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
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib2.urlopen(req).read())

    def _get_public(self, www, uri):
        req = urllib2.Request(www + uri)
        req.add_header("User-Agent", "Bitcoin-exchange-crawler")
        return json.loads(urllib2.urlopen(req).read())

    def getWallet(self):
        www = 'https://cex.io'
        uri = '/api/balance/'

        js = self._get(www, uri, {})

        wallet = {}
        for k, v in js.items():
            if len(k) == 3:
                wallet[k] = float(v["available"]) 
                if "orders" in v:
                    wallet[k] += float(v["orders"])

        return wallet

    def getMarkets(self):
        # Dear cex.io. Please fix your api. Best regards
        return [
            ('GHS', 'BTC'),
            ('LTC', 'BTC'),
            ('NMC', 'BTC'),
            ('GHS', 'NMC'),
            ('IXC', 'BTC'),
            ('GHS', 'USD'),
            ('BTC', 'USD'),
            ('LTC', 'USD')
        ]

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
