#-------------------------------------------------------------------------------
# Name          cryptsy
# Purpose:      Module allows the retrieval of balances from cryptsy
#
# Author:       Jasper van Gelder
#
# Created:      16-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import urllib
import urllib2
import json
import time
import hmac,hashlib
import conversiontable

def getInstance():
    return CryptsyVisitor()

class CryptsyVisitor:
    def __init__(self):
        self._table = None
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'cryptsy'
        except Exception as e:
            return False

    def visit( self, obj,toValueKey='BTC' ):
        api = CryptsyApi( obj['pubkey'], obj['privkey'] )
        #create the currency conversion table
        if not self._table:
            self._buildConversionTable(api)
        #Get the balance data
        try:
            data = api.query_private('getinfo')
        except Exception as e:
            raise Exception("Crypty: "+str(e))
        if int(data['success']):
            ret = data['return']
            balances = dict()
            for (a, b) in ret['balances_available'].items():
                if a not in balances:
                    balances[a] = 0
                balances[a] = balances[a] + float(b)
            if 'balances_hold' in ret:
                for (a, b) in ret['balances_hold'].items():
                    if a not in balances:
                        balances[a] = 0
                    balances[a] = balances[a] + float(b)
            #Calculate the total
            total = 0
            for (key, value) in balances.items():
                try:
                    total += self._table.convert( key,toValueKey, value );
                    #print "total is "+str(total)+" after "+key+"-"+toValueKey+" amount: "+str(value)
                except conversiontable.ConversionException:
                    pass;
            return total
        else:
            raise Exception('Cryptsy error: '+data['error'] )
        
    def _buildConversionTable(self, api):
        #get market values
        try:
            data = api.query_public('marketdatav2')
        except Exception as e:
            raise Exception( str("Crypty "+str(e)) )
        ret = data['return']['markets']
        markets = {}
        for key, item in ret.items():
            #find best buyorder and best sellorder
            sellorders = item['sellorders']
            buyorders = item['buyorders']
            bestsellorder = None
            bestbuyorder = None
            if sellorders is not None:
                for order in sellorders:
                    if not bestsellorder:
                        bestsellorder = float(order['price'])
                    elif order < bestsellorder:
                        bestsellorder = float(order['price'])
            if buyorders is not None:
                for order in buyorders:
                    if not bestbuyorder:
                        bestbuyorder = float(order['price'])
                    elif order > bestbuyorder:
                        bestbuyorder = float(order['price'])
            if bestbuyorder is not None and bestsellorder is not None:
                avg = ( bestbuyorder + bestsellorder ) / 2.0
                diff = abs( bestbuyorder - bestsellorder ) / avg                
                markets[(item['primarycode'],item['secondarycode'])] = (avg, diff )
        self._table = conversiontable.ConversionTable( markets )
        
class CryptsyApi:
    def __init__(self, APIKey, Secret):
        self.APIKey = str(APIKey)
        self.Secret = str(Secret)

    def query_public(self, method ):
        ret = urllib2.urlopen(urllib2.Request(' http://pubapi.cryptsy.com/api.php?method=' + method))
        return json.loads(ret.read())
        
    def query_private(self, method, req={}):
        req['method'] = method
        req['nonce'] = int(time.time()*1000)
        post_data = urllib.urlencode(req)

        sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': self.APIKey
        }

        ret = urllib2.urlopen(urllib2.Request('https://api.cryptsy.com/api', post_data, headers))
        jsonRet = json.loads(ret.read())
        return jsonRet

def main():
    vis = CryptsyVisitor()
    json = { 'type':'cryptsy',
             'name':'cryptsy-test',
             'pubkey':'bogus-public-key',
             'privkey':'aa33153451345134513451345314'}

    assert( vis.accept( json ) )

    print vis.visit( json )

if __name__ == '__main__':
    main()

