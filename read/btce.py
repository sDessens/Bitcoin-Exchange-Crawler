# Module allows the retrieval of balances from BTC-e

import urllib
import urllib2
import json
import time
import hmac,hashlib
from common.resources.partialBalance import PartialBalance
from common.resources.collection import Collection
from common.conversiontable import ConversionTable

import logging
log = logging.getLogger( 'main.read.btce' )

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
        tovalue = "btc"
        table = ConversionTable(api.getMarketsGraph())
        totals = []
        #fix for un synchronized getInfo and ActiveOrders call
        for i in range(3):
            availablefunds = api.calculateAvailableFunds(tovalue,table)
            orderfunds = api.calculateFundsInOrders(tovalue,table)
            totals.append(availablefunds + orderfunds)
            time.sleep(0.01)
        out = Collection()
        out[json['out']] = PartialBalance(sorted(totals)[len(totals)/2])
        return out

class BtceApi:
    def __init__(self, APIKey, Secret):
        self.APIKey = str(APIKey)
        self.Secret = str(Secret)
        
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
                log.error( 'retrying... ({0})'.format(str(retries)) )
                retries += 1
                self.query_private(method,url,req,retries)
            #raise an error if it is an invalid key
            if (int(reply['success']) ==0):
                if (reply['error'] == 'invalid api key') :
                    raise Exception( 'Btce: ' + str( reply['error'] ) + ' after '+str(retries) + ' retries')
                #return None if there are no orders
                elif reply['error'] == 'no orders':
                    return None
                #retry if succes was 0 and retries <= 2
                else:
                    log.warn(reply['error'])
                    log.warn( 'retrying... ({0})'.format(str(retries)) )
                    time.sleep(0.01)
                    retries += 1 
                    retvalue = self.query_private(method,url,req,retries)
                    return retvalue
            elif (int(reply['success']) ==1):
                #return the value if it was succesfully retrieved
                return reply['return']
        else:
            raise Exception( 'Btce: failed after '+str(retries) + ' retries')

    def calculateFundsInOrders(self,tovalue,table):
        #calculate funds stuck in orders
        total =0
        try:
            orders = self.query_private('ActiveOrders','https://btc-e.com/tapi')
        except Exception as e:
            raise
        if orders is not None:
            for orderid, order in orders.iteritems():
                orderpair = order['pair']
                typeOrder = order['type']
                amount = order['amount']
                keys = orderpair.split('_')
                key = keys[0]
                total += table.convert(key, tovalue, amount)
        return total

    def calculateAvailableFunds(self,tovalue,table):
        wallet = None
        try:
            wallet = self.query_private('getInfo','https://btc-e.com/tapi')
        except Exception as e:
            log.error(e.message)
        funds = wallet['funds']
        total =0
        #calculate funds
        if wallet is not None:
            for key, value in funds.iteritems():
                total += table.convert(key, tovalue, value)
        return total

    def getMarketsGraph(self):
        js = self.query_public('https://btc-e.com/api/3/info')
        d = {}
        for key, value in js['pairs'].iteritems():
            keys = key.split("_")
            tickerdata = self.getTicker(key)
            pair = (keys[0], keys[1])
            rate = (float(tickerdata['sell']) + float(tickerdata['buy'])) / 2.0
            cost = (float(tickerdata['sell']) - rate) / rate
            d[pair] = (rate, cost)
        return d

    def getTicker(self,pair):
        ret = self.query_public('https://btc-e.com/api/2/'+pair+'/ticker')
        return ret['ticker']
def main():
    FORMAT = "%(levelname)s\t%(name)s: %(message)s"
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger('main')
    log.setLevel(10)
    jsondata = {'pubkey': 'XC9GJNDH-2H9MMEPK-ASN23UF6-77OYBD5U-0SZHT3G9', 'privkey': '35dbfd7d84c52fb18e1e7ad6011f11fd58ca760e688ef00b322ae7c09a63055b'}
    visitor = BtceVisitor()
    visitordata = visitor.visit(jsondata)
    print str(visitordata)

if __name__ == '__main__':
    main()