# This module implements last week profit kpi this can be added to the report. 
from common.resources.fullBalance import FullBalance
from common.balanceData import BalanceData
from common.resources.collection import Collection

from time import time
from datetime import datetime
import logging
log = logging.getLogger( 'main.process.kpi.lastweekprofitKPIVisitor' )


## This function is required for every Visitor module
def getInstance():
    return lastweekprofitKPIVisitor()

## this is a Process visitor. It provides all required functionality 
#  for an Process visitor
class lastweekprofitKPIVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'lastweekprofit'
        except Exception as e:
            return False
    
    def visit( self, json, resources ):
        balanceCollection = resources.selectMany(json['data'],FullBalance)
        thetime = time()
        week = 7*24*60*60
        profit = 0.0
        for key,balance in balanceCollection:
            profit += balance.value.diff(thetime - week,thetime )
        kpivalue = profit
        indicator = ""
        return (indicator,kpivalue)
