import os
from common.balanceData import BalanceData

import logging
log = logging.getLogger('main.localfile')


class LocalFileStorage:
    def __init__(self, location):
        self.location = location

    def read_content(self, download_file_path):
        full_path = self.location + os.sep + download_file_path
        with open(full_path, 'r') as f:
            return f.read()

    def write_content(self, upload_file_path, content):
        full_path = self.location + os.sep + upload_file_path
        dir = os.path.dirname(full_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(full_path, 'w') as f:
            f.write(content)

    def read_balance(self, balance_id):
        content = self.read_content(balance_id + '.csv')
        timestamps = []
        values = []
        for line in content.split('\n'):
            if line:
                ts, value = line.split(',')
                timestamps.append(float(ts))
                values.append(float(value))

        assert timestamps == sorted(timestamps)
        return BalanceData(timestamps, values)

    def append_balance(self, balance_id, timestamp, value):
        balance_id += '.csv'
        try:
            content = self.read_content(balance_id).encode('utf-8')
        except IOError as e:
            log.warn("Balance id {} does not exist. Creating.".format(balance_id))
            content = ""
        content += "{},{}\n".format(timestamp, value)
        self.write_content(balance_id, content)
