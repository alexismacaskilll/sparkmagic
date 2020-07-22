from requests.auth import AuthBase
import requests

import json
import os
import subprocess
import logging 
import sys

import six

from google.auth import environment_vars
from google.auth import exceptions
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException, GcloudNotInstalledException
from google.cloud import dataproc_v1beta2
import google.auth.transport.requests 
import google.oauth2._client
import google.oauth2.credentials



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
# The command to set all credentialed accounts 
_CLOUD_SDK_SET_CREDENTIALED_ACCOUNT_COMMAND = ("config", "set", "account")
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
    except (OSError) as caught_exc:
        new_exc = GcloudNotInstalledException(
            "Gcloud is not installed" 
        )
        raise new_exc
        #six.raise_from(new_exc, caught_exc)
    #finally: 
    #    return load_json_input(accounts_json)
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Failed to obtain access token"
        )
        raise new_exc
        #six.raise_from(new_exc, caught_exc)

def set_credentialed_account(acconut):
    """Load all of user's credentialed accounts with ``gcloud config set account `ACCOUNT` command.

    
    Raises:
        fill in 
    """
    accounts_json = ""
    if os.name == "nt":
        command = _CLOUD_SDK_WINDOWS_COMMAND
    else:
        command = _CLOUD_SDK_POSIX_COMMAND
    try:
        set_account_command =   ("config", "set", "account", acconut)
        command = (command,) + set_account_command 
        account = subprocess.check_output(command, stderr=subprocess.STDOUT)
        
    except (OSError) as caught_exc:
        new_exc = GcloudNotInstalledException(
            "Gcloud is not installed" 
        )
        raise new_exc
        #six.raise_from(new_exc, caught_exc)
    #finally: 
    #    return load_json_input(accounts_json)
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Failed to obtain access token"
        )
        raise new_exc
        #six.raise_from(new_exc, caught_exc)

def get_component_gateway_url(cluster_name, project_id, region): 
    #project_id, cluster_name = 'google.com:hadoop-cloud-dev', 'amacaskill-livy'
    #region = 'us-central1'
    
    #cluster_name ='amacaskill-livy'
    client = dataproc_v1beta2.ClusterControllerClient(
                       client_options={
                            'api_endpoint': '{}-dataproc.googleapis.com:443'.format(region)
                        }
                    )
    response = client.get_cluster(project_id, region, cluster_name)

    url = ((response.config.endpoint_config).http_ports)['HDFS NameNode']
    index = url.find('.com/')
    index = index + 4
    endpointAddress = url[0: index] + '/gateway/default/livy/v1'
    return endpointAddress




class HTTPGoogleAuth(AuthBase):
    """Attaches HTTP Google Auth Authentication to the given Request
    object."""

    def __init__(self, token = None, accounts = {}, active_account = "", credentials = None, project = ""):
        self.token = token
        self.accounts = list_credentialed_accounts()
        self.active_account = list_active_account()
        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )


        

    
    def __call__(self, request):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logger = logging.getLogger('LOGGER_NAME')

        callable_request = google.auth.transport.requests.Request()
        #checks if the credentials are valid. If they are not that means that either the token = None or it is expired, either way, we refresh. 

        if self.credentials.valid == False:
            self.credentials.refresh(callable_request)
            #access_token, refresh_token, expiry, grant_response = google.oauth2._client.refresh_grant(request, credentials.token_uri, credentials.refresh_token, credentials.client_id, credentials.client_secret)

        logger.info(self.credentials.refresh_token)
        logger.info(self.credentials.expired)
        logger.info(self.credentials.quota_project_id)
        logger.info(self.credentials.token)
        logger.info(self.credentials.expiry)
        
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        return request

   
