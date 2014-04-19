#-------------------------------------------------------------------------------
# Name          DropboxStorage
# Purpose:      Module that provides functionallity to write/read files and
#               balancedata to/from dropbox.
#
# Author:       Jasper van Gelder
#
# Created:      15-04-2014
# Copyright:    (c) Jasper van Gelder 2014
# Licence:      TBD
#-------------------------------------------------------------------------------

import time
import json
import os
import dropbox
import logging
log = logging.getLogger( 'main.dropbox' )

import common.balanceData as balanceData

##
#This class uses dropbox as storage medium.
#
# @param datafolder the dropbox folder the files should be send to
# @param app_key a the public key of you dropbox app
# @param app_secret the secret of your dropbox app<BR>
# \var seperator the separator used for the uploaded files
# All params should be string values<BR>
# Example:<BR>
#   storage = DropboxStorage('/dropboxsubfolder','mydropboxkey','mydropboxsecret')
    
class DropboxStorage:
    def __init__(self,datafolder,app_key,app_secret):
        self.datafolder = datafolder
        self.app_key = app_key
        self.app_secret = app_secret

        self.separator = ","
        self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        self.client= None
        self.session = {}
        
        self.extention = 'csv'
        self.accessTokenFile = 'accesstoken.json'
        """Check if the file alreay exists if not creat it"""
        try:
            with open(self.accessTokenFile, mode='r') as fp:
                self.session = json.loads(fp.read())
        except:
            print "creating file"
            with open(self.accessTokenFile, mode='w') as fp:
                json.dump(self.session,fp)
        self.authorize()

    ##
    # This function authorizes it self with the dropbox server and stores the session key in self.session
    # It also adds it to the file defined in self.accessTokenFile for later use (so the use does not have to constantly
    # authorize himself)
    # \warning Be Aware! this is a security hazzard if the token is compromized an attacker can get full access to your
    # account
    def authorize(self):
        # Have the user sign in and authorize this token
        if not 'access_token' in self.session:
            authorize_url = self.flow.start()
            print '1. Go to: ' + authorize_url
            print '2. Click "Allow" (you might have to log in first)'
            print '3. Copy the authorization code.'
            code = raw_input("Enter the authorization code here: ").strip()
            
            # This will fail if the user enters an invalid authorization code
            access_token, user_id = self.flow.finish(code)
            self.session['access_token'] = access_token
            with open(self.accessTokenFile, mode='w') as fp:
                json.dump(self.session,fp)
        else:
            access_token = self.session['access_token']
        self.client = dropbox.client.DropboxClient(access_token)

    ## Downloads a file from dropbox including metadata
    # @param fullname the path of the file
    # @return dropbox filepointer
    def downloadFile(self,fullname):
        if self.client is None:
            print "No client object"
            return 0
        return self.client.get_file_and_metadata(fullname)

    ## Uploads a file to dropbox through the use of a filepointer
    #   @param filepointer
    #   @param uploadname the name underwhich to upload the file
    #   @param overwrite bool if the file should be overwriten or not
    #
    def writeFilePTR(self, filepointer,uploadname):
        response = self.client.put_file(self.datafolder+'/'+uploadname, filepointer,overwrite)
    
    ## Uploads a file to dropbox through the use of a filepath
    #   @param localpath path to the file that should be uploaded, relative to current dir
    #   @param uploadname the name under which to upload the file
    def writeFile(self, localpath ,uploadname):
        with open(localpath, 'rb') as fp:
            response = self.client.put_file(self.datafolder+uploadname, fp,True)

    ##The readBalance function that downloads the balanceData and returns a BalanceData object
    # @param identifier a string that identifies the file it will be written to.
    # @param fromTime the timeStamp from which the data should be returned
    # @param toTime the until what timeStamp data should be fetched
    # @return BalanceData the object that contains the balance data and timestamp in the period given by fromTime,toTime
    def readBalance(self,identifier,fromTime=0,toTime=2000000000):
        if self.client is None:
            print "No client object"
            return 0
        filename=identifier+'.'+self.extention
        fullname = self.datafolder+'/'+filename

        timestamps= []
        balance=[]

        try:
            fp = self.downloadFile(fullname)
        except dropbox.client.ErrorResponse as e:
            log.error( 'while downloading file {0}: {1}'.format( fullname, str(e) ) )
            raise Exception()

        for line in fp[0]:
            values = line.split(self.separator)
            time = int(values[0])
            if  time > fromTime and time < toTime:
                timestamps.append(time)
                balance.append(float(values[1]))
        return balanceData.BalanceData(timestamps,balance)

    ##The writeBalance function that adds the blance value to the file in dropbox
    # @param identifier a string that identifies the file it will be written to.
    # @param value the value that should be writen
    def writeBalance(self,identifier,value):
        timestamp = int(time.time())
        filename=identifier+'.'+self.extention

        folder_metadata = self.client.metadata(self.datafolder)
        filepointer = open('temp.csv~','w+')
        filepaths = []
        #if the file already exists download it else create it
        for entry in folder_metadata['contents']:
            if entry['path'].find(filename) != -1:
                print entry['path']
                restdata, metadata = self.downloadFile(entry['path'])
                filepointer.write(restdata.read())
                break
        filepointer.write(str(timestamp)+","+str(value)+"\n")
        filepointer.seek(0)
        response = self.client.put_file(self.datafolder+'/'+filename, filepointer,True)
        filepointer.close()
        if os.path.isfile('temp.csv~'):
            os.remove('temp.csv~')
