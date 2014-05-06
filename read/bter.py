# Module allows query of balances from Bter


import json
import urllib
import urllib2
import time
import hashlib
import hmac
import logging
log = logging.getLogger('main.exchanges.bter')

import common.conversiontable as conversiontable
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection


def getInstance():
    return BterVisitor()

class BterVisitor:
    def __init__(self):
        self._table = None
        pass

    def accept(self, json):
        try:
            return json['type'] == 'bter'
        except Exception as e:
            return False

    def visit( self, json ):
        api = BterApi( json['pubkey'], json['privkey'] )
        if self._table is None:
            self._table = self._buildConversionTable(api)

        balance = api.query_private( 'getfunds', {} )
        total = 0.0

        if 'locked_funds' in balance:
            for k, v in balance['locked_funds'].items():
                total += self._convert( k, 'BTC', float(v) )

        if 'available_funds' in balance:
            for k, v in balance['available_funds'].items():
                total += self._convert( k, 'BTC', float(v) )

        out = Collection()
        out[json['name']] = PartialBalance( total )
        return out

    def _buildConversionTable(self, api):
        tickers = api.query_public('tickers')

        markets = dict()

        for k, v in tickers.items():
            buy = float(v['buy'])
            sell = float(v['sell'])
            avg = ( buy + sell ) / 2.0
            diff = abs( buy - sell ) / avg

            primary, secondary = k.upper().split('_')
            markets[(primary, secondary)] = ( avg, 1.0 + diff )

        return conversiontable.ConversionTable( markets )

    def _convert(self, fromStock, toStock, amount):
        try:
            result = self._table.convert(fromStock.upper(), toStock.upper(), amount)
            return result
        except conversiontable.ConversionException as e:
            log.info( e )
            return 0


class BterApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def post(self, path, params, headers = {}):
        url = 'https://data.bter.com' + path
        post = urllib.urlencode( params )
        headers['user-agent'] = 'Mozilla/5.0'
        ret = urllib2.urlopen(urllib2.Request( url, post, headers ))
        return json.loads(ret.read())

    def get(self, path, headers = {}):
        url = 'https://data.bter.com' + path
        headers['user-agent'] = 'Mozilla/5.0'
        req = urllib2.urlopen( urllib2.Request( url, headers=headers ) )
        return json.loads(req.read())

    def query_public(self, method, retry = 4 ):
        uri = '/api/1/' + method
        for _ in range(retry):
            try:
                return self.get( uri )
            except:
                pass
        raise


    def query_private(self, method, params, retry = 4):
        uri = '/api/1/private/' + method
        params['nonce'] = int(time.time()*1000)
        post = urllib.urlencode( params )
        signature = hmac.new( self.priv, post, hashlib.sha512 )
        headers = dict(Sign=signature.hexdigest(), Key=self.pub)
        for _ in range(retry):
            try:
                data = self.post( uri, params, headers )
                if data['result'] == 'false':
                    raise Exception( 'Bter: ' + data['message'] )
                return data
            except:
                pass
        raise

def main():
    vis = BterVisitor()
    json = { 'type':'bter',
             'name':'bter-test',
             'pubkey':'bogus-public-key',
             'privkey':'aa33153451345134513451345314'}

    assert( vis.accept(json) )

    print vis.visit( json )

if __name__ == '__main__':
    main()
