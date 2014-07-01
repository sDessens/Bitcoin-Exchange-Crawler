# This module implements last period profit kpi this can be added to the report. 
from common.resources.fullBalance import FullBalance
from common.balanceData import BalanceData
from common.resources.collection import Collection

from time import time
from datetime import datetime
import logging
log = logging.getLogger( 'main.process.kpi.fullbalancevalueVisitor' )


## This function is required for every Visitor module
def getInstance():
    return fullbalancevalueKPIVisitor()

## this is a Process visitor. It provides all required functionality 
#  for an Process visitor
class fullbalancevalueKPIVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'fullbalancevalue'
        except Exception as e:
            return False
    ##returns the current balance
    # @param json a json variable containing: a resource string,
    # @param resources a resource object
    def visit( self, json, resources ):
        balance = resources.selectOne(json['data'],FullBalance)
        thetime = time()
        kpivalue = 0.0
        kpivalue = balance.value.interpolate(thetime)
        indicator = ""
        return (indicator,kpivalue)
