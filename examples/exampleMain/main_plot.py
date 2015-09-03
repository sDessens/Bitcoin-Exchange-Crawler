from read.localfileReadVisitor import LocalFileBalanceHistory
from common.balanceData import  BalanceData

import matplotlib.pyplot as plt

from process.matplotlibpdf import MatplotlibVisitor

files = LocalFileBalanceHistory('foo')

balance = files.visit('btce')

print balance
for k, v in balance.items():
    print k, v



fig, ax = plt.subplots()

ax.plot(balance.timestampsAsDateTime(), balance.balance())


fig.show()


from time import sleep
sleep(4)