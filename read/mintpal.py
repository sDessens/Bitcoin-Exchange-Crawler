# Module allows the retrieval of balances from Mintpal

import json
import urllib2
import time
import hashlib
import hmac
import logging
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

log = logging.getLogger( 'main.exchanges.mintpal' )

def getInstance():
    return MintpalVisitor()

class MintpalVisitor:
    def __init__(self):
        pass

    def accept( self, json ):
        try:
            return json['type'] == 'mintpal'
        except Exception as e:
            return False

    def visit( self, json ):
        api = MintpalApi( json['pubkey'], json['privkey'] )
        out = Collection()
        wallet = api.getWallet()
        table = ConversionTable(api.getMarketsGraph())
        total = 0
        for k, v in wallet.items():
            total += table.convert(k, 'BTC', v)
        out[json['out']] = PartialBalance( total )
        return out

class MintpalApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def _get(self, url):
        url += '?time={}'.format(str(int(time.time())))
        url += '&key={}'.format(self.pub)
        url += '&hash={}'.format(hmac.new(self.priv, url, hashlib.sha256).digest().encode('hex'))
        ret = urllib2.urlopen(urllib2.Request(url))
        return json.loads(ret.read())

    def getWallet(self):
        js = self._get('https://api.mintpal.com/v2/wallet/balances/')
        d = {}
        for payload in js['data']:
            k = payload['code']
            v = float(payload['balance_pending_withdraw']) + \
                float(payload['balance_held']) + \
                float(payload['balance_pending_deposit']) + \
                float(payload['balance_available'])
            d[k] = v
        return d

    def getMarketsGraph(self):
        js = self._get('https://api.mintpal.com/v2/market/summary/')
        d = {}
        for payload in js['data']:
            pair = (payload['code'], payload['exchange'])
            rate = (float(payload['top_ask']) + float(payload['top_bid'])) / 2.0
            cost = (float(payload['top_ask']) - rate) / rate
            d[pair] = (rate, cost)
        return d