from lastBalance.okcoin import OkcoinLastBalance
from lastBalance.btcchina import BtcChinaLastBalance
from lastBalance.btce import BtceLastBalance
from lastBalance.cryptsy import CryptsyLastBalance
from lastBalance.bter import BterLastBalance
from lastBalance.cex import CexLastBalance
from lastBalance.hitbtc import HitbtcLastBalance
from lastBalance.kraken import KrakenLastBalance
from lastBalance.mintpal import MintpalLastBalance

from write.dropboxWriteVisitor import DropboxAppendBalance
from write.localFileWriteVisitor import LocalFileWriteVisitor

import traceback
import logging

FORMAT = "%(levelname)s\t%(name)s: %(message)s"
logging.basicConfig(format=FORMAT)


exchanges = [
    ('okcoin', OkcoinLastBalance('123', '456')),
    ('btcchina', BtcChinaLastBalance('123', '456')),
    ('btce', BtceLastBalance('123', '456')),
    ('cryptsy', CryptsyLastBalance('123', '456')),
    ('bter', BterLastBalance('123', '456')),
    ('cex', CexLastBalance('123', '456', 'myUserName')),
    ('hitbtc', HitbtcLastBalance('123', '456')),
    ('kraken', KrakenLastBalance('123', '456')),
    ('mintpal', MintpalLastBalance('123', '456'))
]

storage = LocalFileWriteVisitor('foo')

for k, v in exchanges:
    try:
        print 'now crawling', k
        total = v.crawl()
        print 'total:', total
        storage.visit(k, total)
    except Exception as e:
        print 'exception:', e
        print traceback.format_exc()

