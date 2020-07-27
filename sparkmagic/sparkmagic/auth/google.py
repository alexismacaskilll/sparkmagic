from requests.auth import AuthBase
from .customauth import Authenticator


import requests

import json
import os
import subprocess

import six

from google.auth import environment_vars
from google.auth import exceptions
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException
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
        sparkmagic.livyclientlib.GcloudNotInstalledException: if gcloud is not installed
        sparkmagic.livyclientlib.BadUserConfigurationException: if account is not set or user needs to run gcloud auth login
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
        """
    except (OSError) as caught_exc:
        new_exc = GcloudNotInstalledException(
            "Gcloud is not installed" 
        )
        raise new_exc
        """
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = BadUserConfigurationException(
            #add gcloud auth login / set account message.  
            "Failed to obtain access token. "
        )
        raise new_exc

def set_credentialed_account(account):
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
        set_account_command =   ("config", "set", "account", account)
        command = (command,) + set_account_command 
        active_account = subprocess.check_output(command, stderr=subprocess.STDOUT)
        """
    except (OSError) as caught_exc:
        new_exc = GcloudNotInstalledException(
            "Gcloud is not installed" 
        )
        raise new_exc
        """
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Failed to obtain access token"
        )
        raise new_exc

def get_component_gateway_url(cluster_name, project_id, region): 
    """Gets the component gateway url for a cluster name, project id, and region

    Args:
        cluster_name (str): The cluster name to use for the url
        project_id (str): The project id to use for the url
        region (str): The project id to use for the url
       
    Returns:
        str: the component gateway url

    Raises:
        google.api_core.exceptions.GoogleAPICallError: If the request failed for any reason.
        google.api_core.exceptions.RetryError: If the request failed due to a retryable error and retry attempts failed.
        ValueError: If the parameters are invalid.
    """
    client = dataproc_v1beta2.ClusterControllerClient(
                       client_options={
                            'api_endpoint': '{}-dataproc.googleapis.com:443'.format(region)
                        }
                    )
    try:
        response = client.get_cluster(project_id, region, cluster_name)
        url = ((response.config.endpoint_config).http_ports)['HDFS NameNode']
        index = url.find('.com/')
        index = index + 4
        endpointAddress = url[0: index] + '/gateway/default/livy/v1'
        return endpointAddress
    except: 
        raise

"""
class HTTPGoogleAuth(AuthBase):
    #Attaches HTTP Google Auth Authentication to the given Request object.

    def __init__(self, token = None, accounts = {}, active_account = "", credentials = None, project = ""):
        self.token = token
        #self.accounts = list_credentialed_accounts()
        #self.active_account = list_active_account()

        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )


    
    def __call__(self, request):
        callable_request = google.auth.transport.requests.Request()
        #valid is in google.auth.credentials, not oauth2 so make sure this is doing the right thing
        if self.credentials.valid == False:
            self.credentials.refresh(callable_request)
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        return request

"""   

class GoogleAuth(Authenticator):
    """Custom Authenticator to use Google OAuth with SparkMagic."""

    #overrides Authenticators endpoint widgets because it needs to show the project ID, cluster name, region and credentials dropdown. 
    def show_correct_endpoint_fields(self): 
        #don't think I need address widget layout because parent has it. but we will see. 
        self.address.widget.layout.display = 'flex'
        self.google_credentials_widget.layout.display = 'flex'
        self.cluster_name_widget.layout.display = 'flex'
        self.address_widget.layout.display = 'none'
        self.project_widget.layout.display = 'flex'
        self.region_widget.layout.display = 'flex'
    #def get_widgets(self): 

    """

    google_api_url = "https://www.googleapis.com/oauth2/v4/token"
    

    
    def _token_url_default(self):
        return "%s/oauth2/v4/token" % (self.google_api_url)
    
    def _scope_default(self):
        return ['openid', 'email']

    
    name = "Google"
    REDIRECT_STATE = False
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/revoke'
    REVOKE_TOKEN_METHOD = 'GET'
    # The order of the default scope is important
    DEFAULT_SCOPE = ['openid', 'email', 'profile']
    DEPRECATED_DEFAULT_SCOPE = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('expires_in', 'expires'),
        ('token_type', 'token_type', True)
    ]
    """

    def authenticate(self):
        
        """Authenticate a user with login form data
        It must return dict on successful authentication,
        and return None on failed authentication. self.login_service
        is not none, must override this in subclass
        
        Args:
            handler (tornado.web.RequestHandler): the current request handler
            data (dict): The formdata of the login form.
                        The default form has 'username' and 'password' fields.
        Returns:
            user (dict or None):
                The Authenticator may return a dict instead, which MUST have a
                key `login_service` holding the login_service, and other optional 
                keys the auth_type requires like tokens for google auth, user names / 
                passwords. 
        """
        callable_request = google.auth.transport.requests.Request()

        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )
        if self.credentials.valid == False:
            self.credentials.refresh(callable_request)
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        
        return {
            u"login_service": self.login_service,
            u"request": request
        }
        







    def __init__(self, token = None, accounts = {}, active_account = "", credentials = None, project = ""):
        self.token = token
        self.accounts = list_credentialed_accounts()
        self.active_account = list_active_account()

        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )



    
    """
    def list_active_account(self): 
        if self.active_account is None: 
            self.credentials(refresh) 
        active_account = self.credentials.id_token

        try: 
            accounts = list_credentialed_accounts()
            for account in accounts:
                if account['status'] == "ACTIVE": 
                    return account['account']
            return ""
        except: 
            raise
    """
    
    def __call__(self, request):
        callable_request = google.auth.transport.requests.Request()
        #valid is in google.auth.credentials, not oauth2 so make sure this is doing the right thing
        if self.credentials.valid == False:
            self.credentials.refresh(callable_request)
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        return request

    
   