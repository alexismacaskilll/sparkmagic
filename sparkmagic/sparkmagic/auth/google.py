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
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
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
        endpointAddress = url[0: index] + '/gateway/default/livy/v1'
        return endpointAddress
    except: 
        raise



class GoogleAuth(Authenticator):
    """Custom Authenticator to use Google OAuth with SparkMagic."""

    def __init__(self):
        self.login_service = u"Google"
        self.url = 'http://example.com/livy'
        self.widget_width = "800px"
        
    def show_correct_endpoint_fields(self): 
        self.address_widget.layout.display = 'flex'

    def hide_correct_endpoint_fields(self): 
        self.address_widget.layout.display = 'none'

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
            value = list_active_account(),
            description=u"Account:"
        )

        widgets = {self.project_widget, self.cluster_name_widget, self.region_widget, self.google_credentials_widget}
        return widgets 

    def update_url(self): 
        self.url = get_component_gateway_url(self.project_widget.value,self.cluster_name_widget.value, self.region_widget.value)
   
    def __call__(self, request):
        callable_request = google.auth.transport.requests.Request()
        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )

        #valid is in google.auth.credentials, not oauth2 so make sure this is doing the right thing
        if self.credentials.valid == False:
            self.credentials.refresh(callable_request)
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        return request

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
        """callable_request = google.auth.transport.requests.Request()
        

        self.credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform','https://www.googleapis.com/auth/userinfo.email' ] )
        if self.credentials.valid == False:
            self.credentials.refresh(callable_request)
        

        
        request.headers['Authorization'] = 'Bearer {}'.format(self.credentials.token)
        
        return {
            u"login_service": self.login_service,
            u"request": request
        }
        """
        


   