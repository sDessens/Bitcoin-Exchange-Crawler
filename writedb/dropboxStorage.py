import json
import tempfile
import os
import time

import dropboxReadVisitor

from balanceData import *

def getInstance():
    return DropboxStorageVisitor()

class DropboxStorageVisitor:
    def __init__(self):
        pass

    def accept( self, obj ):
        try:
            return obj['type'] == 'dropboxstorage'
        except Exception as e:
            return False

    def visit( self, obj ):
        storage = DropboxStorage(obj['folder'],obj['separator'], obj['app_key'], obj['app_secret'] )
        return storage

##
#This class uses dropbox as storage medium.
#
# @param datafolder the dropbox folder the files should be send to
# @param seperator the separator used for the uploaded files
# @param app_key a the public key of you dropbox app
# @param app_secret the secret of your dropbox app<BR>
# All params should be string values<BR>
# Example:<BR>
#   storage = DropboxStorage('/dropboxsubfolder','mydropboxkey','mydropboxsecret')
    
class DropboxStorage:
    def __init__(self,datafolder,separator,app_key,app_secret):
        """
            @var accessTokenFile the file where the access token should be saved
        """
        self.datafolder = datafolder
        self.separator = separator
        self.app_key = app_key
        self.app_secret = app_secret
        
        self.flow = dropboxReadVisitor.client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
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
        self.client = dropboxReadVisitor.client.DropboxClient(access_token)
    ## Downloads a file from dropbox including metadata
    # @param filepath string the dropbox path to the file including the filename
    #
    def downloadFile(self,filepath):
        if self.client is None:
            print "No client object"
            return 0 
        return self.client.get_file_and_metadata(filepath)
    ##Uploads a file to dropbox
    #   @param filepath string the path to the file including the filename
    #   @param uploadname the name underwhich to upload the file
    #   @param overwrite bool if the file should be overwriten or not
    #
    def uploadFile(self, filepath,uploadname,overwrite):
        f = open(filepath, 'rb')
        response = self.client.put_file(self.datafolder+uploadname, f,overwrite)

    ##The read function that downloads the data and returns a BalanceData object
    # @param identifier a string that identifies the file it will be written to.
    # @param fromTime the timeStamp from which the data should be returned
    # @param toTime the until what timeStamp data should be fetched
    def read(self,identifier,fromTime,toTime):
        if self.client is None:
            print "No client object"
            return 0
        filename='/'+identifier+'.'+self.extention
        timestamps= []
        balance=[]
        fp = self.downloadFile(self.datafolder+filename)
        for line in fp[0]:
            values = line.split(self.separator)
            time = int(values[0])
            if  time > fromTime and time < toTime:
                timestamps.append(time)
                balance.append(float(values[1]))
        return BalanceData(timestamps,balance)

    ##The write function that adds the value to the file in dropbox
    # @param identifier a string that identifies the file it will be written to.
    # @param value the value that should be writen
    def write(self,identifier,value):
        timestamp = int(time.time())
        filename='/'+identifier+'.'+self.extention

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
        response = self.client.put_file(self.datafolder+filename, filepointer,True)
        filepointer.close()
        if os.path.isfile('temp.csv~'):
            os.remove('temp.csv~')
        
