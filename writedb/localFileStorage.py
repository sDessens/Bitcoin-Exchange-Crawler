import os
import tempfile
import time
import common.balanceData as balanceData

def getInstance():
    return LocalFileStorageVisitor()

class LocalFileStorageVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'localfilestorage'
        except Exception as e:
            return False

    def visit( self, obj ):
        storage = LocalFileStorage(ob['folder'],obj['separator'])
        return storage

##
#This class uses local storage as medium.
#
# @param location the dropbox folder the files should be send to
# @param seperator the separator used for the uploaded files
# All params should be string values
# Example:
#   storage = LocalFileStorage('/mysubfolder',',')
#   this will store the files in mysubfolder with values separated by ','
  
class LocalFileStorage:
    def __init__(self,location,separator):
        self.location = location
        self.separator = separator
        
    ##The write function that adds the value to the file in the given folder
    # @param identifier a string that identifies the file it will be written to.
    # @param value the value that should be writen
    def write(self, identifier, value):
        timestamp = int(time.time())
        filename = '/'+identifier+'.csv'
        try:
            with open(self.location+filename, mode='a') as fp:
                fp.write(str(timestamp) +self.separator+str(value))
        except:
            print "creating file"
            with open(self.location+filename, mode='w') as fp:
                fp.write(str(timestamp) +self.separator+str(value))

    ##The read function that downloads the data and returns a BalanceData object
    # @param identifier a string that identifies the file it will be written to.
    # @param fromTime the timeStamp from which the data should be returned
    # @param toTime the until what timeStamp data should be fetched
    def read(self, identifier, fromTime=0,toTime=int(0xFFFFFFFFFF)):
        timestamps = []
        balance = []
        filename = '/'+identifier+'.csv'
        try:
            with open(self.location+filename, mode='r') as fp:
                for line in fp:
                    values = line.split(self.separator)
                    time = int(values[0])
                    if  time > fromTime and time < toTime:
                        timestamps.append(time)
                        balance.append(float(values[1]))
                return BalanceData(timestamps,balance)
        except Exception as e:
            print e
            print "No data for this section found"
