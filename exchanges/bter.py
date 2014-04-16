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


def getInstance():
    return BterVisitor()

class BterVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'bter'
        except Exception as e:
            return False

    def visit( self, obj ):
        api = BterApi( obj['pubkey'], obj['privkey'] )
        ret = api.query_private( 'TradeBalance', { 'asset' : 'XBTC' } )
        if 'result' in ret:
            return ret['result']['tb']
        else:
            raise Exception( 'Kraken: ' + str( ret['error'] ) )


class BterApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv

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
    print ret

if __name__ == '__main__':
    main()
