#-------------------------------------------------------------------------------
# Name          kraken
# Purpose:      Module allows the retrieval of balances from Kraken
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
import base64
import logging

log = logging.getLogger( 'main.exchanges.kraken' )

def getInstance():
    return KrakenVisitor()

class KrakenVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'kraken'
        except Exception as e:
            return False

    def visit( self, obj ):
        api = KrakenApi( obj['pubkey'], obj['privkey'] )
        ret = api.query_private( 'TradeBalance', { 'asset' : 'XBTC' } )
        if 'result' in ret:
            return ret['result']['tb']
        else:
            log.error( '{0} {1}'.format(obj['name'], str( ret['error']) ) )
            raise Exception(  )

class KrakenApi:
    def __init__(self, pub, priv):
        self.pub = pub
        self.priv = priv

    def query(self, path, params, headers = {}):
        url = 'https://api.kraken.com' + path
        post = urllib.urlencode( params )
        headers['user-agent'] = 'bot'
        ret = urllib2.urlopen(urllib2.Request( url, post, headers ))
        return json.loads(ret.read())

    def query_public(self, method, params):
        return self.query( '/0/public/' + method, params )

    def query_private(self, method, params):
        url = 'https://api.kraken.com/'
        path = '/0/private/' + method

        params['nonce'] = int(time.time()*1000)
        post = urllib.urlencode( params )
        message = path + hashlib.sha256(str(params['nonce']) + post).digest()
        signature = hmac.new(base64.b64decode(self.priv), message, hashlib.sha512)
        headers = {
            'API-Key': self.pub,
            'API-Sign': base64.b64encode(signature.digest())
        }

        return self.query( path, params, headers )


def main():
    vis = KrakenVisitor()
    json = { 'type':'kraken',
             'name':'kraken-test',
             'pubkey':'bogus-public-key',
             'privkey':'5555555555555555555555555555555555555555555555555555555555555555555555555555555555555Q=='}

    assert( vis.accept( json ) )

    print vis.visit( json )

if __name__ == '__main__':
    main()
