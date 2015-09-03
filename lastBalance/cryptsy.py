# Module allows the retrieval of balances from cryptsy
import urllib
import urllib2
import json
import time
import hmac,hashlib
import logging
from common.conversiontable import ConversionTable

log = logging.getLogger('main.exchanges.cryptsy')


class CryptsyLastBalance:
    def __init__(self, pubkey, privkey):
        self._pubkey = pubkey
        self._privkey = privkey

    def crawl(self):
        api = CryptsyApi(self._pubkey, self._privkey)
        table = self._buildConversionTable(api)

        data = api.query_private('getinfo')

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
                total += table.convert_or_null(key, 'btc', value)

            return total
        else:
            log.error('cryptsy api call returned success = 0')
            raise
            return 0

    def _buildConversionTable(self, api):
        #get market values
        data = api.query_public('marketdatav2')

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

        self._table = ConversionTable( markets )
        
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