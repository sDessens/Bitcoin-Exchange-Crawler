# This module implements last period profit kpi this can be added to the report. 
from common.resources.fullBalance import FullBalance
from common.balanceData import BalanceData
from common.resources.collection import Collection

from time import time
from datetime import datetime
import logging
log = logging.getLogger( 'main.process.kpi.lastperiodprofitVisitor' )


## This function is required for every Visitor module
def getInstance():
    return lastperiodprofitKPIVisitor()

## this is a Process visitor. It provides all required functionality 
#  for an Process visitor
class lastperiodprofitKPIVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'lastperiodprofit'
        except Exception as e:
            return False
    ##returns the profit from a certain period till now
    # @param json a json dict containing data: a list of resource strings,
    # period: the amount of seconds to the last period form now. A day = 24*60*60,
    # @param resources a resource object
    def visit( self, json, resources ):
        balanceCollection = resources.selectMany(json['data'],FullBalance)
        thetime = time()
        period = json['period']
        profit = 0.0
        for key,balance in balanceCollection:
            profit += balance.value.diff(thetime - period,thetime)
        kpivalue = profit
        indicator = ""
        return (indicator,kpivalue)
