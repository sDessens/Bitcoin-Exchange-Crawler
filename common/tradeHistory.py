# these functions can be used to convert the account trading history
# to something that is the same for all exchanges
# which allows common analyzer scipts to work on all exchanges,

import json
import datetime
from pytz import timezone
import dateutil.parser

utc = timezone('UTC')


def create_trade(ts, pair, price, amount, trade_type):
    assert(trade_type in ('buy', 'sell'))
    return {
        'time': ts,
        'action': 'trade',
        'pair': pair,
        'price': price,
        'amount': amount,
        'type': trade_type,
    }


class BtceAccountHistoryLoader:
    def parse_timestamp(self, timestamp):
        return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)

    def load(self, content):
        trades = json.loads(content)
        mutations = []

        for key in sorted(trades.keys()):
            trade_info = trades[key]
            order_id = trade_info['order_id']
            # print order_id,
            ts = self.parse_timestamp(float(trade_info['timestamp']))
            amount = trade_info['amount']
            rate = trade_info['rate']
            pair = trade_info['pair']
            type = trade_info['type']  # buy or sell

            mutations.append(create_trade(ts, pair, rate, amount, type))

        return mutations


class YobitAccountHistoryLoader(BtceAccountHistoryLoader):
    pass


class CexCsvAccountHistoryLoader:
    def parse_timestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

    def load(self, content):
        mutations = []
        for line in content.split('\n'):
            ts, _, _, _, type, pair, _, _, comment = line.split(',')
            _, amount, _, _, price, _ = comment.strip().split(' ')
            mutations.append(create_trade(self.parse_timestamp(ts),
                                          pair.lower().replace('/', '_'),
                                          float(price),
                                          float(amount),
                                          type))

        return mutations


class CexAccountHistoryLoader:
    def parse_timestamp(self, timestamp):
        return dateutil.parser.parse(timestamp)

    def load(self, content):
        mutations = []
        o = json.loads(content)
        for key, trades in o.items():
            key = key.lower().replace('/', '_')
            for trade in trades:
                mutations.append(create_trade(self.parse_timestamp(trade['lastTxTime']),
                                              key,
                                              float(trade['price']),
                                              float(trade['amount']) - float(trade['remains']),
                                              trade['type']))
        return mutations


class KrakenAccountHistoryLoader:
    PAIRS = {
        'XETHZEUR': 'eth_usd',
        'XETHXXBT': 'eth_btc',
        'XXBTZEUR': 'btc_usd',
        'XETCXETH': '111_111'
        }

    def parse_timestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp[:timestamp.find('.')], "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

    def load(self, content):
        mutations = []
        for line in content.split('\n')[1:]:  # skip header row
            _, _, pair, time, type, _, price, _, _, vol, _, _, _, _ = line.replace('"', '').split(',')
            mutation = {'time': self.parse_timestamp(time),
                        'action': 'trade',
                        'pair': self.PAIRS[pair],
                        'price': float(price),
                        'amount': float(vol),
                        'type': type}  # buy / sell

            mutations.append(mutation)

        return mutations


class BitfinexAccountHistoryLoader:
    PAIRS = {
        'BFXUSD': '111_111',
        'BTCUSD': 'btc_usd',
        'ETHUSD': 'eth_usd',
        'ETHBTC': 'eth_btc',
        'ETCBTC': 'etc_btc',
        'ETCUSD': 'etc_usd',
    }

    def parse_timestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

    def load(self, content):
        mutations = []
        for line in content.split('\n')[1:]:  # skip header row
            tid, pair, amount, price, date = line.split(',')
            mutation = {'time': self.parse_timestamp(date),
                        'action': 'trade',
                        'pair': self.PAIRS[pair],
                        'price': float(price),
                        'amount': abs(float(amount)),
                        'type': 'buy' if float(amount) > 0 else 'sell'}
            mutations.append(mutation)

        mutations.sort(key=lambda x: x['time'])
        return mutations


class PoloniexCsvAccountHistoryLoader:
    PAIRS = {
        'BTC/USDT': 'btc_usd',
        'ETH/USDT': 'eth_usd',
        'ETH/BTC': 'eth_btc',
        'ETC/BTC': 'etc_btc',
        'ETC/USDT': 'etc_usd',
        'ETC/ETH': 'etc_eth',
        'LSK/BTC': 'lsk_btc',
    }

    def parse_timestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

    def load(self, content):
        mutations = []
        for line in content.split('\n')[1:]:  # skip header row
            date, pair, _, type, price, amount, _, _, _, _, _ = line.split(',')
            mutation = {'time': self.parse_timestamp(date),
                        'action': 'trade',
                        'pair': self.PAIRS[pair],
                        'price': float(price),
                        'amount': abs(float(amount)),
                        'type': 'buy' if type == 'Buy' else 'sell'}

            mutations.append(mutation)

        mutations.sort(key=lambda x: x['time'])
        return mutations


class PoloniexJsonAccountHistoryLoader:
    def parse_timestamp(self, timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)

    def load(self, content):
        mutations = []
        for key, value in json.loads(content).items():
            pair = '_'.join(key.lower().split('_')[::-1])
            for trade in value:
                mutations.append(create_trade(
                    self.parse_timestamp(trade['date']),
                    pair,
                    float(trade['rate']),
                    float(trade['amount']),
                    trade['type']
                ))

        mutations.sort(key=lambda x: x['time'])
        return mutations


class BitfinexJsonAccountHistoryLoader:
    def parse_timestamp(self, timestamp):
        return datetime.datetime.utcfromtimestamp(float(timestamp)).replace(tzinfo=utc)

    def load(self, content):
        mutations = []

        for key, value in json.loads(content).items():
            pair = (key[:3] + '_' + key[3:]).lower()
            for trade in value:
                mutations.append(create_trade(
                    self.parse_timestamp(trade['timestamp']),
                    pair,
                    float(trade['price']),
                    abs(float(trade['amount'])),
                    trade['type'].lower(),
                ))

        mutations.sort(key=lambda x: x['time'])
        return mutations
