import tempfile
import os
import atexit

## contains a list of (os-handle, name, python-handle)
__files = list()

## generate a temp file
#  return path
def generateTempFile( autodelete ):
    oh, path = tempfile.mkstemp()

    if autodelete == True:
        __files.append( (oh, path) )

    return path


def freeResources():
    print 'clearing temp files'
    while len( __files ):
        oh, path = __files.pop()
        print '  del', path
        os.close( oh )
        os.remove( path )

atexit.register( freeResources )


