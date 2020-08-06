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
from hdijupyterutils.ipythondisplay import IpythonDisplay
from google.oauth2.credentials import Credentials

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
        pass

def list_accounts_pairs(): 
    """Reformates all of user's credentialed accounts to populate google_credentials_widget dropdown's options. 

    Returns:
        dict: each key is a str of the users credentialed accounts and it maps to the same str credentialed account
    """
    accounts = list_credentialed_accounts()
    accounts_list = {}
    for account in accounts:
        accounts_list[account['account']] = account['account']
    if application_default_credentials_configured():
        accounts_list['default-credentials'] = 'default-credentials'
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

def get_credentials_for_account(account, scopes):
    """Load all of user's credentialed accounts with ``gcloud auth describe ACCOUNT`` command.

    Args:
        account (str): user credentialed account to return credentials for
        scopes (Sequence[str]): list of scopes to include in the credentials.
    
    Returns:
        google.oauth2.credentials.Credentials: The constructed credentials

    Raises:
        ValueError: If `gcloud auth describe ACCOUNT --format json` returns json not in the expected format.
        sparkmagic.livyclientlib.BadUserConfigurationException: if account is not set or user needs to run gcloud auth login
        or if gcloud is not installed. 
    """
    accounts_json = ""
    if os.name == "nt":
        command = _CLOUD_SDK_WINDOWS_COMMAND
    else:
        command = _CLOUD_SDK_POSIX_COMMAND
    try:
        
        ipython_display = IpythonDisplay()
        describe_account_command = ("auth", "describe", account, '--format', 'json')
        command = (command,) + describe_account_command

        account_json = subprocess.check_output(command, stderr=subprocess.STDOUT)
        ipython_display.writeln(account_json)
        account_describe = load_json_input(account_json)
        
        ipython_display.writeln(account_describe)

        return Credentials.from_authorized_user_info(account_describe)
    except ValueError: 
        raise
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


def application_default_credentials_configured(): 
    """Checks if google application-default credentials are configured"""
    callable_request = google.auth.transport.requests.Request()
    credentials, project = google.auth.default()
    try:
        credentials.refresh(callable_request) 
    except (DefaultCredentialsError, RefreshError) as error:
            return False
    return True


class GoogleAuth(Authenticator):
    """Custom Authenticator to use Google OAuth with SparkMagic."""

    def __init__(self):
        self.callable_request = google.auth.transport.requests.Request()
        self.active_account = list_active_account()
        self.credentials, self.project_id = None, None
        try: 
            self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )
            self.credentials.refresh(self.callable_request) 
        except (DefaultCredentialsError, RefreshError) as error: 
            self.credentials, self.project = None, None
        #Authenticator.__init__(self)
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
            options=list_accounts_pairs(),
            value = None,
            description=u"Account:"
        )

        #set account dropdown to currently active credentialed user account, if there is one. 
        if self.active_account is not None: 
            self.google_credentials_widget.value = self.active_account
        #set account dropdown to default-credentials if application-default credentials are configured
        elif application_default_credentials_configured(): 
            self.google_credentials_widget.value = 'default-credentials'
        else: 
            self.google_credentials_widget.disabled = True
        
        widgets = [self.project_widget, self.cluster_name_widget, self.region_widget, self.google_credentials_widget]
        return widgets

    def initialize_credentials_with_auth_account_selection(self): 
        """Initializes self.credentials with the accound selected from the auth dropdown widget"""
        if (self.google_credentials_widget.value == 'default-credentials'): 
            self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )
            self.credentials.refresh(self.callable_request)
        else: 
            set_credentialed_account(self.google_credentials_widget.value)
            self.credentials = self.get_credentials_for_account(self.google_credentials_widget.value, scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )
            self.credentials.refresh(self.callable_request)

    def update_with_widget_values(self): 
        new_exc = ValueError(
                    "Could not generate component gateway url with project id: {}, cluster name: {}, region: {}"\
                        .format(self.project_widget.value, self.cluster_name_widget.value, self.region_widget.value)
                )
        if (self.credentials is not None):
            try: 
                self.url = get_component_gateway_url(self.project_widget.value, self.cluster_name_widget.value, self.region_widget.value)
            except: 
                raise new_exc
        else: 
            raise new_exc
        self.initialize_credentials_with_auth_account_selection()

    def __call__(self, request):
        if self.credentials.valid == False:
            self.credentials.refresh(self.callable_request)
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        return request
