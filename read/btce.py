#-------------------------------------------------------------------------------
# Name          btce
# Purpose:      Module allows the retrieval of balances from BTC-e
#
# Author:       Jasper van Gelder
#
# Created:      15-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import urllib
import urllib2
import json
import time
import hmac,hashlib
from common.writeable.partialBalance import PartialBalance
from common.writeable.collection import Collection

def getInstance():
    return BtceVisitor()

class BtceVisitor:
    def __init__(self):
        pass

    def accept(self, json):
        try:
            return json['type'] == 'btce'
        except Exception as e:
            return False

    def visit( self, json ):
        api = BtceApi( json['pubkey'], json['privkey'] )
        wallet = None
        try:
            wallet = api.query_private('getInfo','https://btc-e.com/tapi')
        except Exception as e:
            raise
        funds = wallet['funds']
        btcTotal =0
        tovalue = "btc"
        #calculate funds
        if wallet is not None:
            for key, value in funds.iteritems():
                if value != 0 :
                    if key != tovalue:
                        pair = api.getPair(key,tovalue)
                        avg = api.getAvg(pair)
                        if pair.startswith(key):
                            btcTotal += value * avg
                        else:
                            btcTotal += value /avg
                    else:
                        btcTotal += value
        #calculate funds stuck in orders
        try:
            orders = api.query_private('ActiveOrders','https://btc-e.com/tapi')
        except Exception as e:
            raise
        if orders is not None:
            for orderid, order in orders.iteritems():
                orderpair = order['pair']
                typeOrder = order['type']
                amount = order['amount']
                keys = orderpair.split('_')
                key = keys[0]               
                if key != tovalue:
                    pair = api.getPair(key,tovalue)
                    avg = api.getAvg(pair)
                    if pair.startswith(key):
                        btcTotal += amount * avg
                    else:
                        btcTotal += amount /avg
                else:
                    btcTotal += amount

        out = Collection()
        out[json['name']] = btcTotal
        return out

class BtceApi:
    def __init__(self, APIKey, Secret):
        self.APIKey = str(APIKey)
        self.Secret = str(Secret)
        self.Pairs = []
        self.fillPairs()
        
    def query_public(self,url):
        ret = urllib2.urlopen(url)
        jsonRet = json.loads(ret.read())
        return jsonRet

    def query_private(self, method,url, req={},retries =0):
        req['method'] = method
        req['nonce'] = int(time.time())
        post_data = urllib.urlencode(req)

        sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': self.APIKey
        }
        #try to send the request and retrieve data
        if retries < 3:
            try:
                ret = urllib2.urlopen(urllib2.Request(url, post_data, headers))
                reply = json.loads(ret.read())
            #retry if the request failed
            except:
                print str(retries)+ " retrying..."
                retries += 1
                self.query_private(method,url,req,retries)
            #raise an error if it is an invalid key
            if (int(reply['success']) ==0):
                if (reply['error'] == 'invalid api key') :
                    raise Exception( 'Btce: ' + str( reply['error'] ) + ' after '+str(retries) + ' retries')
                #return None if there are no orders
                elif reply['error'] != 'no orders':
                    return None
                #retry if succes was 0 and retries <= 2
                else:
                    print str(retries)+ " retrying..."
                    time.sleep(1)
                    retries += 1 
                    self.query_private(method,url,req,retries)
            elif (int(reply['success']) ==1):
                #return the value if it was succesfully retrieved
                return reply['return']
        else:
            raise Exception( 'Btce: failed after '+str(retries) + ' retries')    
        
    def fillPairs(self):
        jsonret = self.query_public('https://btc-e.com/api/3/info')
        pairs = jsonret['pairs']
        for key, value in pairs.iteritems():
            self.Pairs.append(key)
    
    def getPair(self,code1,code2):
        for pair in self.Pairs:
            if code1 in pair and code2 in pair:
                return pair
        return "notfound"
    
    def getAvg(self,pair):
        ret = self.query_public('https://btc-e.com/api/2/'+pair+'/ticker')
        return ret['ticker']['avg']

def main():
    obj = {"pubkey": "I2R9TAKF-IIKOFCN3-THOTOQSW-P84KZ2UG-PD27E7YU","privkey":"a751e0559833d1c4544c3f5873995e2c5ea72413cc5e7a809caeddb0f3607535"}
    try:
        print BtceVisitor().visit(obj)
    except Exception as e:
        print e
if __name__ == '__main__':
    main()