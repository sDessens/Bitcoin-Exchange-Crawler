# -Module that provides functionallity to write/read files and
# balancedata to/from dropbox.
from dropbox.exceptions import ApiError

import common.tempFileLib
import json
import dropbox
import dropbox.files

import logging

log = logging.getLogger('main.dropbox')
import time

import common.balanceData as balanceData


##
# This class uses dropbox as storage medium.
#
# @param datafolder the dropbox folder the files should be send to
# \var seperator the separator used for the uploaded files
# All params should be string values<BR>
# Example:<BR>
#   storage = DropboxStorage('/dropboxsubfolder')

class DropboxStorage:
    def __init__(self, datafolder):
        self.datafolder = datafolder
        if not self.datafolder.endswith('/'):
            self.datafolder += '/'

        self.separator = ","
        self.client = None
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
                json.dump(self.session, fp)
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
            print '1. Go to: https://www.dropbox.com/developers/apps'
            print '2. Create an app.'
            print '2. Copy the App key.'
            app_key = raw_input("Enter the App key here: ").strip()
            print '2. Copy the App secret.'
            app_secret = raw_input("Enter the App secret here: ").strip()
            flow = dropbox.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

            authorize_url = flow.start()
            print '1. Go to: ' + authorize_url
            print '2. Click "Allow" (you might have to log in first)'
            print '3. Copy the authorization code.'
            code = raw_input("Enter the authorization code here: ").strip()

            # This will fail if the user enters an invalid authorization code
            access_token, user_id = flow.finish(code)
            self.session['access_token'] = access_token
            print 'Access to dropbox can be saved for automation purpose'
            print 'If you do save it it will be stored in ' + self.accessTokenFile
            print 'Be aware that this file gives access to your dropbox account, so better protect it!'
            save = None
            yes = ['y', 'yes']
            inputs = yes + ['no', 'n']
            while save not in inputs:
                save = raw_input('Do you want to store access to this dropbox account [y/n] ()').strip().lower()
                if save not in inputs:
                    print 'posible inputs ' + str(inputs)
            if save in yes:
                with open(self.accessTokenFile, mode='w') as fp:
                    json.dump(self.session, fp)
        else:
            access_token = self.session['access_token']
        self.client = dropbox.Dropbox(access_token)

    def read_content(self, download_file_path):
        assert self.client
        path = '/' + self.datafolder + download_file_path
        return self.client.files_download(path)[1].text

    def write_content(self, upload_file_path, content):
        assert self.client
        path = '/' + self.datafolder + upload_file_path
        self.client.files_upload(content, path, dropbox.files.WriteMode('overwrite', None), True)

    def read_balance(self, balance_id):
        assert self.client
        content = self.read_content(balance_id + '.csv')
        timestamps = []
        values = []
        for line in content.split('\n'):
            if line:
                ts, value = line.split(',')
                timestamps.append(float(ts))
                values.append(float(value))

        assert timestamps == sorted(timestamps)
        return balanceData.BalanceData(timestamps, values)

    def append_balance(self, balance_id, timestamp, value):
        assert self.client
        balance_id += '.csv'
        try:
            content = self.read_content(balance_id).encode('utf-8')
        except ApiError as e:
            log.warn("Balance id {} does not exist. Creating.".format(balance_id))
            if not e.error.get_path().is_not_found():
                raise
            content = ""
        content += "{},{}\n".format(timestamp, value)
        self.write_content(balance_id, content)
