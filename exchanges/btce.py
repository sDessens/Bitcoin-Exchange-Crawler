#!/bin/env/python
import urllib
import urllib2
import json
import time
import hmac,hashlib
from datetime import datetime

def getInstance():
    return BtceVisitor()

class BtceVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'btce'
        except Exception as e:
            return False

    def visit( self, obj ):
        api = BtceApi( obj['pubkey'], obj['privkey'] )
        try:
            wallet = api.query_private('getInfo','https://btc-e.com/tapi')
        except Exception as e:
            raise e
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
            raise e
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
        return btcTotal

class BtceApi:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret
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

        ret = urllib2.urlopen(urllib2.Request(url, post_data, headers))
        reply = json.loads(ret.read())
        while not reply['success']:
            #raise an error after 10 faulty replies
            if not reply['success'] and retries > 2 :
                raise Exception( 'Btce: ' + str( reply['error'] ) + ' after '+str(retries) + ' retries')
            #return the value if it was succesfully retrieved
            elif reply['success']:
                return reply['return']
            #retry if succes was 0 and retries <= 10
            else:
                print str(retries)+ " retrying..."
                time.sleep(1)
                retries += 1 
                reply = self.query_private(method,url,req,retries)
        return reply['return']             
        
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
    obj = {"pubkey": "pub","privkey":"priv"}
    try:
        print BtceVisitor().visit(obj)
    except Exception as e:
        print e
if __name__ == '__main__':
    main()
