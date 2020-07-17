from requests.auth import AuthBase
import requests

import json
import os
import subprocess

import six

from google.auth import environment_vars
from google.auth import exceptions
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException, GcloudNotInstalledException


# The ~/.config subdirectory containing gcloud credentials.
_CONFIG_DIRECTORY = "gcloud"
# Windows systems store config at %APPDATA%\gcloud
_WINDOWS_CONFIG_ROOT_ENV_VAR = "APPDATA"
# The name of the file in the Cloud SDK config that contains default
# credentials.
_CREDENTIALS_FILENAME = "application_default_credentials.json"
# The name of the Cloud SDK shell script
_CLOUD_SDK_POSIX_COMMAND = "gcloud"
_CLOUD_SDK_WINDOWS_COMMAND = "gcloud.cmd"
# The command to get the Cloud SDK configuration
_CLOUD_SDK_CONFIG_COMMAND = ("config", "config-helper", "--format", "json")
# The command to get google user access token
_CLOUD_SDK_USER_ACCESS_TOKEN_COMMAND = ("auth", "print-access-token")
# The command to get all credentialed accounts 
_CLOUD_SDK_USER_CREDENTIALED_ACCOUNTS_COMMAND = ("auth", "list", "--format", "json")
# Cloud SDK's application-default client ID
CLOUD_SDK_CLIENT_ID = (
    "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"
)

def load_json_input(result):
    """Load json data from the file."""
    jsondata = None
    try:
        jsondata = json.loads(result)
    except:
        pass
    return jsondata

def list_active_account(): 
    try: 
        accounts = list_credentialed_accounts()
        for account in accounts:
            if account['status'] == "ACTIVE": 
                return account['account']
        return ""
    except: 
        raise

def list_accounts_pairs(): 
    try: 
        accounts = list_credentialed_accounts()
        accounts_list = {}
        for account in accounts:
            accounts_list[account['account']] = account['account']
        return accounts_list
    except: 
        raise
    
def list_credentialed_accounts():
    """Load all of user's credentialed accounts with ``gcloud auth list`` command.

    Returns:
        list: the users credentialed accounts 

    Raises:
        Maybe if gcloud isnt installed
        google.auth.exceptions.UserAccessTokenError: if failed to get access
            token from gcloud...
    """
    accounts_json = ""
    if os.name == "nt":
        command = _CLOUD_SDK_WINDOWS_COMMAND
    else:
        command = _CLOUD_SDK_POSIX_COMMAND
    try:
        command = (command,) + _CLOUD_SDK_USER_CREDENTIALED_ACCOUNTS_COMMAND
        accounts_json = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return load_json_input(accounts_json)
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = exceptions.BadUserConfigurationException(
            "Failed to obtain access token"
        )
        raise new_exc
        #six.raise_from(new_exc, caught_exc)
    except (OSError) as caught_exc:
        new_exc = exceptions.GcloudNotInstalledException(
            "Gcloud is not installed" 
        )
        raise new_exc
        #six.raise_from(new_exc, caught_exc)
    #finally: 
    #    return load_json_input(accounts_json)


    

class HTTPGoogleAuth(AuthBase):
    """Attaches HTTP Google Auth Authentication to the given Request
    object."""

    def __init__(self, token = None, accounts = {}, active_account = ""):
        self.token = token
        self.accounts = list_credentialed_accounts()
        self.active_account = list_active_account()

    
    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return request

   
