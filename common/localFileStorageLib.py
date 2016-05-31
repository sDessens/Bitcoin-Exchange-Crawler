# Module that provides functionallity to write/read files and
# balancedata to/from local file storage.


import os
import shutil
import time
from common.balanceData import BalanceData
import logging
log = logging.getLogger( 'main.localfile' )


##
#This class uses local storage as medium.
#
# @param location the dropbox folder the files should be send to
# \var self.seperator the separator used for the uploaded files
# All params should be string values
# Example:
#   storage = LocalFileStorage('/mysubfolder')
#   this will store the files in mysubfolder with values separated by ','
  
class LocalFileStorage:
    def __init__(self,location):
        self.location = location
        self.separator = ","
        
    ##The write function that adds the balance value to the file in the given folder
    # @param identifier a string that identifies the file it will be written to.
    # @param value the value that should be writen
    def append_balance(self, identifier, timestamp, value):
        timestamp = int(timestamp)
        filepath = self.location+'/'+identifier+'.csv'
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        try:
            with open(filepath, mode='a') as fp:
                fp.write(str(timestamp) +self.separator+str(value)+'\n')
        except:
            log.info('creating file {0}'.format(filepath))
            with open(filepath, mode='w') as fp:
                fp.write(str(timestamp) +self.separator+str(value)+'\n')

    ##The read function that downloads the balancedata and returns a BalanceData object
    # @param identifier a string that identifies the file it will be written to.
    # @param fromTime the timeStamp from which the data should be returned
    # @param toTime the until what timeStamp data should be fetched
    # @return BalanceData the object that contains the balance data and timestamp in the period given by fromTime,toTime
    def readBalance(self, identifier, fromTime=0,toTime=int(0xFFFFFFFFFF)):
        timestamps = []
        balance = []
        
        filepath = self.location+'/'+identifier+'.csv'
        try:
            with open(filepath, mode='r') as fp:
                for line in fp:
                    values = line.split(self.separator)
                    time = int(values[0])
                    if  time > fromTime and time < toTime:
                        timestamps.append(time)
                        balance.append(float(values[1]))
                return BalanceData(timestamps,balance)
        except Exception as e:
            log.error( 'failed to parse {0}'.format(identifier) )

    ##  Writes the file to local storage
    #   @param filepath a path to a local file
    #   @param uploadfilepath a path to the target destination of the file
    def writeFile(self, filepath, uploadfilepath):
        uploadfilepath = self.location + os.sep + uploadfilepath
        dirname = os.path.dirname(uploadfilepath)
        if not os.path.exists( dirname ):
            os.makedirs(dirname)
        shutil.copyfile( filepath, uploadfilepath )
