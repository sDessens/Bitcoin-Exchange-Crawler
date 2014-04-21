#-------------------------------------------------------------------------------
# Name          stub
# Purpose:      Module is stub implementation of WriteDB Visitor.
#               Developers can use this file as an example when implementing
#               additional writeable objects
#
# Author:       Stefan Dessens
#
# Created:      17-04-2014
# Copyright:    (c) Stefan Dessens 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

from common.writeable.partialBalance import PartialBalance
from common.writeable.fullBalance import FullBalance
from common.writeable.file import File
from common.writeable.mail import Mail

import logging
log = logging.getLogger( 'main.write.stub' )


def getInstance():
    return StubWriteVisitor()


## this is a stub write visitor. It provides an template that provides all
#  required functionality for an storage visitor
class StubWriteVisitor:
    def __init__(self):
        pass

    ## check if visitor accepts given object
    #  @return true if object is accepted
    def accept( self, json ):
        try:
            return json['type'] == 'stub'
        except Exception as e:
            return False

    ## write the object to the storage specified in json
    #  @param json block of implementation defined json data
    #  @param resources an instance of common.writable.collection
    #  may throw an exception.
    def visit(self, json, resources):
        for key in json['data']:
            if key not in resources:
                log.error( 'attempting to write resource {0}, but no such resource exists'.format(key) )
                continue
            resource = resources[key]
            log.debug( 'writing resource {0} : {1}'.format( key, str(resource) ) )
            print