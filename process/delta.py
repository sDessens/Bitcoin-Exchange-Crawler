# Calculates the derivative of any FullBalance resource


import common.balanceData as balanceData
from common.resources.fullBalance import FullBalance
import traceback
import logging
log = logging.getLogger( 'main.process.delta' )


## This function is required for every Visitor module
def getInstance():
    return DeltaVisitor()

class DeltaVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    #  may not return exceptions
    def accept( self, json ):
        try:
            return json['type'] == 'delta'
        except Exception as e:
            return False

    ## run the delta algorithm.
    #  @param json contains implementation defined information about the process type
    #  @param resources contains array of common.writable.*
    #  @return the full, post-processed, list of resources
    #  may return exception
    def visit( self, json, resources ):
        for section in json['data']:
            try:
                input = resources[section['in']]
                days = section['days'] if 'days' in section else 1
                if isinstance(input, FullBalance):
                    resources[section['out']] = FullBalance( input.value.generateDiff( float(days) ) )
                else:
                    log.error( 'attempt to calculate delta over resource {0}, but is of incorrect type {1}'
                        .format(section['in'], input.__class__.__name__ ) )
            except:
                log.error( 'unable to generate diff based on section {0}'.format(section) )
                log.debug( traceback.format_exc() )

        return resources