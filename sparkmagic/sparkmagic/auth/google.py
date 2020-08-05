from .customauth import Authenticator
import json
import os
import subprocess
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException
from sparkmagic.utils.constants import WIDGET_WIDTH
from google.cloud import dataproc_v1beta2
import google.auth.transport.requests 
from google.auth import _cloud_sdk  
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory

# The name of the Cloud SDK shell script
_CLOUD_SDK_POSIX_COMMAND = "gcloud"
_CLOUD_SDK_WINDOWS_COMMAND = "gcloud.cmd"
# The command to get all credentialed accounts 
_CLOUD_SDK_USER_CREDENTIALED_ACCOUNTS_COMMAND = ("auth", "list", "--format", "json")

def load_json_input(result):
    """Load json data from the file."""
    jsondata = None
    try:
        jsondata = json.loads(result)
    except:
        pass
    return jsondata

def list_active_account(): 
    """Returns the active account from all the user's credentialed accounts that are listed 
    with the ``gcloud auth list`` command. Used to set the google_credentials_widget dropdown
    to be the active account on load. 

    Returns:
        str: the active account from the user's credentialed accounts or an empty str if no accounts 
        are active.  

    Raises:
        sparkmagic.livyclientlib.BadUserConfigurationException: if account is not set or user needs to run gcloud auth login
        or if gcloud is not installed. 
    """
    try: 
        accounts = list_credentialed_accounts()
        for account in accounts:
            if account['status'] == "ACTIVE": 
                return account['account']
        return None
    except: 
        raise

def list_accounts_pairs(): 
    """Reformates all of user's credentialed accounts to populate google_credentials_widget dropdown's options. 

    Returns:
        dict: each key is a str of the users credentialed accounts and it maps to the same str credentialed account 

    Raises:
        sparkmagic.livyclientlib.BadUserConfigurationException: if account is not set or user needs to run gcloud auth login
        or if gcloud is not installed. 
    """
    accounts = list_credentialed_accounts()
    accounts_list = {}
    for account in accounts:
        accounts_list[account['account']] = account['account']
    return accounts_list

def set_credentialed_account(account):
    """Sets the user's credentialed accounts with ``gcloud config set account `ACCOUNT` command.
    Raises:
         sparkmagic.livyclientlib.BadUserConfigurationException: if account is not set to a valid account, if the user needs  \ 
         to run gcloud auth login, or if gcloud is not installed. 
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
    except (OSError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Gcloud is not installed. Install the Google Cloud SDK." 
        )
        raise new_exc
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Failed to obtain access token. Run `gcloud auth login` in your command line \
            to authorize gcloud to access the Cloud Platform with Google user credentials to authenticate. Run `gcloud auth \
            application-default login` cquire new user credentials to use for Application Default Credentials."
        )
        raise new_exc

  
def list_credentialed_accounts():
    """Load all of user's credentialed accounts with ``gcloud auth list`` command.

    Returns:
        list: each key is a str of one of the users credentialed accounts

    Raises:
        sparkmagic.livyclientlib.BadUserConfigurationException: if account is not set or user needs to run gcloud auth login
        or if gcloud is not installed. 
    """
    accounts_json = ""
    if os.name == "nt":
        command = _CLOUD_SDK_WINDOWS_COMMAND
    else:
        command = _CLOUD_SDK_POSIX_COMMAND
    try:
        command = (command,) + _CLOUD_SDK_USER_CREDENTIALED_ACCOUNTS_COMMAND
        accounts_json = subprocess.check_output(command, stderr=subprocess.STDOUT)
        all_accounts = load_json_input(accounts_json)
        credentialed_accounts = list()
        for account in all_accounts:
            try: 
                _cloud_sdk.get_auth_access_token(account['account'])
                credentialed_accounts.append(account)
            except: 
                pass
        return credentialed_accounts
    except (OSError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Gcloud is not installed. Install the Google Cloud SDK." 
        )
        raise new_exc
    except (subprocess.CalledProcessError, IOError) as caught_exc:
        new_exc = BadUserConfigurationException(
            "Failed to obtain access token. Run `gcloud auth login` in your command line \
            to authorize gcloud to access the Cloud Platform with Google user credentials to authenticate. Run `gcloud auth \
            application-default login` cquire new user credentials to use for Application Default Credentials."
        )
        raise new_exc

    
def get_component_gateway_url(project_id, cluster_name, region): 
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
        endpoint_address = url[0: index] + '/gateway/default/livy/v1'
        return endpoint_address
    except: 
        raise


class GoogleAuth(Authenticator):
    """Custom Authenticator to use Google OAuth with SparkMagic."""

    def __init__(self):
        Authenticator.__init__(self)
        self.callable_request = google.auth.transport.requests.Request()
        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )
        try: 
            self.credentials.refresh(self.callable_request)
        except (DefaultCredentialsError, RefreshError) as error: 
            self.credentials, self.project = None, None

        #valid is in google.auth.credentials, not oauth2 so make sure this is doing the right thing
        self.url = 'http://example.com/livy'
        self.widgets = self.get_widgets(WIDGET_WIDTH)
        
    def get_widgets(self, widget_width): 
        ipywidget_factory = IpyWidgetFactory()

        self.project_widget = ipywidget_factory.get_text(
            description='Project:',
            width=widget_width
        )

        self.cluster_name_widget = ipywidget_factory.get_text(
            description='Cluster:',
            width=widget_width
        )

        self.region_widget = ipywidget_factory.get_text(
            description='Region:',
            width=widget_width
        )

        self.google_credentials_widget = ipywidget_factory.get_dropdown(
            options= list_accounts_pairs(),
            value = None,
            description=u"Account:"
        )

        #set credentialed account dropdown to be the account with status 'ACTIVE' 
        # in accounts returned by `gcloud auth list`
        active_account = None
        try: 
            active_account = list_active_account()
        except BadUserConfigurationException: 
            pass

        if active_account is not None: 
            self.google_credentials_widget.value = active_account
        else: 
            self.google_credentials_widget.disabled = True
        
        widgets = [self.project_widget, self.cluster_name_widget, self.region_widget, self.google_credentials_widget]
        return widgets

    def update_with_widget_values(self): 
        if (self.credentials is not None):
            self.url = get_component_gateway_url(self.project_widget.value,self.cluster_name_widget.value, self.region_widget.value)
        else: 
            raise DefaultCredentialsError
        set_credentialed_account(self.google_credentials_widget.value)
   
    def __call__(self, request):
        if self.credentials.valid == False:
            self.credentials.refresh(self.callable_request)
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        return request