# module implements process visitor that allows summing multiple
# FullBalance resources together.


import common.balanceData as balanceData
from common.resources.fullBalance import FullBalance

import logging
log = logging.getLogger( 'main.process.multiply' )

def getInstance():
    return MultiplyVisitor()

## MultiplyVisitor is an class that allows multiplying multiple BalanceData objects.
class MultiplyVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'multiply'
        except Exception as e:
            return False

    ## run the process algorithm.
    #  this stub printing algorithm prints the identifier and final value of each
    #  BalanceData to stdout.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  @return the full, post-processed, list of resources
    #  may return exception
    def visit( self, json, resources ):
        for key, inputs in json['data'].items():
            try:
                resources[key] = self._sumBalance( resources, inputs )
            except Exception as e:
                log.error( e )
                pass

        return resources


    def _sumBalance(self, resources, inputs):
        arr = []

        for input in inputs:
            if input in resources:
                res = resources[input]
                if isinstance( res, FullBalance ):
                    arr.append( res.value )
                else:
                    log.error( 'resource named {0} is of incorrect type'.format(input))
            else:
                log.error('resource {0} does not exist'.format(input))

        if len(arr) == 0:
            raise Exception( 'No resources of {0} found'.format(inputs) )

        return FullBalance( balanceData.multiply( arr ) )