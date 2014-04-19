
import urllib2
import json
import common.balanceData as balanceData

import logging
log = logging.getLogger( 'main.read.blockchain' )




class BlockchainReadAddressIntoBalanceData:
    def __init__(self):
        pass

    def parse(self, addr):
        data = self._query(addr)

        balance = []
        currentBalance = 0

        transactions = [ t for t in data['txs'] ]
        transactions.sort( key=lambda x: x['time'] )

        for transaction in transactions:
            for input in transaction['inputs']:
                if input['prev_out']['addr'] == addr:
                    currentBalance = 0

            for output in transaction['out']:
                if output['addr'] == addr:
                    currentBalance = currentBalance + output['value'] / 100000000.0

            time = transaction['time']
            balance.append( (time, currentBalance) )

        if len( balance ) == 0:
            raise Exception( 'empty blockchain balance' )

        balance.sort()

        # transform timestamps such that [ a, b, c ] -> [ a-1, a, b-1, b, c-1, c ]
        stamps = [ balance[x/2][0] - ( ~x % 2 ) for x in range(len(balance)*2)]
        # transform values such that [ a, b, b ] -> [ 0, a, a, b, b, c ]
        values = [0] + [ balance[x/2][1] for x in range(len(balance)*2-1)]

        return balanceData.BalanceData( stamps, values )

    def _query(self, addr, retry = 3):
        for _ in range(retry):
            url = 'https://blockchain.info/address/{0}?format=json'.format(addr)
            try:
                req = urllib2.urlopen( urllib2.Request( url, headers={'user-agent': 'Mozilla/5.0'} ) )
                return json.loads(req.read())
            except Exception as e:
                log.error( 'error querying blockchain.info: {0}'.format(str(e)) )
        raise
