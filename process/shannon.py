# Calculates the shannon profit of any FullBalance resource


import common.balanceData as balanceData
from common.resources.fullBalance import FullBalance
import traceback
import logging
log = logging.getLogger( 'main.process.shannon' )


## This function is required for every Visitor module
def getInstance():
    return ShannonVisitor()

class ShannonVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept(self, json):
        try:
            return json['type'] == 'shannon'
        except Exception as e:
            return False

    ## run the delta algorithm.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  @return the full, post-processed, list of resources
    #  may return exception
    def visit(self, json, resources):
        reference = resources[json['reference']]

        updated = {}

        for new, old in json['data'].items():
            try:
                updated[new] = self._shannon(resources[old].value, reference.value)
            except BaseException as e:
                log.error(e)
                pass

        for k, v in updated.items():
            resources[k] = v
        return resources


    def _shannon(self, origin, reference):
        usd = balanceData.multiply([origin, reference])
        usd = usd.generateRelativeDiff()
        origin = origin.generateRelativeDiff()

        return FullBalance(balanceData.sum([usd, origin]))
