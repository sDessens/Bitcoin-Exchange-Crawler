#-------------------------------------------------------------------------------
# Name          kraken
# Purpose:      Module allows query of balances from Kraken
#
# Author:       Stefan Dessens
#
# Created:      15-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import json
import urllib
import urllib2
import time
import hashlib
import hmac

import conversiontable


def getInstance():
    return BterVisitor()

class BterVisitor:
    def __init__(self):
        self._table = None
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'bter'
        except Exception as e:
            return False

    def visit( self, obj ):
        api = BterApi( obj['pubkey'], obj['privkey'] )
        if not self._hasConversionTable():
            self._buildConversionTable(api)

        balance = api.query_private( 'getfunds', {} )
        total = 0.0

        if 'locked_funds' in balance:
            for k, v in balance['locked_funds'].items():
                total += self._convert( k, 'BTC', float(v) )

        if 'available_funds' in balance:
            for k, v in balance['available_funds'].items():
                total += self._convert( k, 'BTC', float(v) )

        return total

    def _buildConversionTable(self, api):
        tickers = None
        for _ in range( 4 ):
            try:
                tickers = api.query_public('tickers')
                break
            except:
                print 'network failed, retry...'
                pass #retry

        if tickers is None:
            raise( 'Bter: network query failed' )

        markets = dict()

        for k, v in tickers.items():
            buy = float(v['buy'])
            sell = float(v['sell'])
            avg = ( buy + sell ) / 2.0
            diff = abs( buy - sell ) / avg

            primary, secondary = k.upper().split('_')
            markets[(primary, secondary)] = ( avg, diff )

        self._table = conversiontable.ConversionTable( markets )

    def _hasConversionTable(self):
        return self._table is not None

    def _convert(self, fromStock, toStock, amount):
        try:
            result = self._table.convert(fromStock.upper(), toStock.upper(), amount)
            return result
        except Exception as e:
            print 'Bter: unable to convert', fromStock, 'to', toStock
            return 0


class BterApi:
    def __init__(self, pub, priv):
        self.pub = str(pub)
        self.priv = str(priv)

    def query(self, path, params, headers = {}):
        url = 'https://data.bter.com' + path
        post = urllib.urlencode( params )
        headers['user-agent'] = 'Mozilla/5.0'
        ret = urllib2.urlopen(urllib2.Request( url, post, headers ))
        return json.loads(ret.read())

    def query_public(self, method ):
        uri = '/api/1/' + method
        return json.loads( urllib2.urlopen( 'https://data.bter.com' + uri ).read() )

    def query_private(self, method, params):
        uri = '/api/1/private/' + method
        params['nonce'] = int(time.time()*1000)
        post = urllib.urlencode( params )
        signature = hmac.new( self.priv, post, hashlib.sha512 )
        headers = dict(Sign=signature.hexdigest(), Key=self.pub)
        return self.query( uri, params, headers )


def main():
    api = BterApi( '806C4D49-8483-438F-8BCD-C91F0F34FB25',
                'ed25a34efa5e9be8a485965cc32d363e1c048fae8872d7df73ff9bc7ea38902a' )

    ret = api.query_public( 'tickers' )
    print ret

    ret = api.query_private( 'getfunds', {} )
    print ret.keys()
    print ret['locked_funds']
    print ret['available_funds']
    print ret

    visitor = BterVisitor()
    visitor._buildConversionTable(api)

if __name__ == '__main__':
    main()
