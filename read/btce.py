# Module allows the retrieval of balances from BTC-e

import urllib
import profile
from urllib3 import connection_from_url
import json
import time
import hmac, hashlib
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
        except BaseException as e:
            return False

    def visit( self, json ):
        api = BtceApi( json['pubkey'], json['privkey'],"btc")
        totals = []
        #fix for incorrect total value because of un synchronized getInfo and ActiveOrders call
        for i in range(3):
            availablefunds = api.calculateAvailableFunds()
            orderfunds = api.calculateFundsInOrders()
            totals.append(availablefunds + orderfunds)
            time.sleep(0.01)
        out = Collection()
        out[json['out']] = PartialBalance(sorted(totals)[len(totals)/2])
        return out

class BtceApi:
    def __init__(self, APIKey, Secret,tovalue):
        self.APIKey = str(APIKey)
        self.Secret = str(Secret)
        self.toValue = tovalue
        self.nonce = int(time.time())
        self.http_pool = connection_from_url('https://btc-e.com')
        self.table = ConversionTable(self.getMarketsGraph())
        
    def query_public(self,uri):
        ret = self.http_pool.request('GET',uri)
        jsonRet = json.loads(ret.data)
        return jsonRet

    def query_private(self, method,uri, req={}):
        req['method'] = method
        req['nonce'] = self.nonce
        post_data = urllib.urlencode(req)
        self.nonce += 1

        sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
        headers = {
            'Sign': sign,
            'Key': self.APIKey
        }

        try:
            ret = self.http_pool.request_encode_body('POST', uri, fields=req, headers=headers)
            reply = json.loads(ret.data)
        #retry if the request failed
        except BaseException as e:
            log.error(e.message)
        #raise an error if it is an invalid key
        if (int(reply['success']) == 0):
            if (reply['error'] == 'invalid api key') :
                raise BaseException( 'Btce: ' + str( reply['error'] ))
            #return None if there are no orders
            elif reply['error'] == 'no orders':
                return None
            #retry if succes was 0 and retries <= 2
            else:
                log.error(reply['error'])
        elif (int(reply['success']) == 1):
            #return the value if it was succesfully retrieved
            return reply['return']

    def calculateFundsInOrders(self):
        #calculate funds stuck in orders
        total = 0
        try:
            orders = self.query_private('ActiveOrders','/tapi')
        except BaseException as e:
            raise
        if orders is not None:
            for orderid, order in orders.iteritems():
                orderpair = order['pair']
                amount = order['amount']
                keys = orderpair.split('_')
                key = keys[0]
                total += self.table.convert(key, self.toValue, amount)
        return total

    def calculateAvailableFunds(self):
        wallet = None
        try:
            wallet = self.query_private('getInfo','/tapi')
        except BaseException as e:
            log.error(e.message)
        funds = wallet['funds']
        total = 0
        #calculate funds
        if wallet is not None:
            for key, amount in funds.iteritems():
                total += self.table.convert(key, self.toValue, amount)
        return total

    def getMarketsGraph(self):
        js = self.query_public('/api/3/info')
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
        ret = self.query_public('/api/2/'+pair+'/ticker')
        return ret['ticker']
