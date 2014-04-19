#-------------------------------------------------------------------------------
# Name          LocalFileStorage
# Purpose:      Module that provides functionallity to write/read files and
#               balancedata to/from local file storage.
#
# Author:       Jasper van Gelder
#
# Created:      17-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------
import os
import time
from common.balanceData import BalanceData

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
    def writeBalance(self, identifier, value):
        timestamp = int(time.time())
        filepath = self.location+'/'+identifier+'.csv'
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        try:
            with open(filepath, mode='a') as fp:
                fp.write(str(timestamp) +self.separator+str(value))
        except:
            print "creating file"
            with open(filepath, mode='w') as fp:
                fp.write(str(timestamp) +self.separator+str(value))

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
            print e
            print "No data for this section found"
    ##  Reads a file from local storage
    #   @param identifier the name of the file
    #   @return returns the data from file
    def readFile(self, identifier):
        try:
            with open(self.location+'/'+identifier, mode='r') as fp:
                return fp.read()
        except:
            raise
    ##  Writes the file to local storage
    #   @param filepointer
    #   @param uploadname the name underwhich to upload the file
    def writeFile(self, filepointer,identifier):
        filepath = self.location+'/'+identifier
        #create the directory if it does not exists yet
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        try:
            with open(filepath, mode='w') as fp:
                fp.write(filepointer.read())
        except:
            raise
    
