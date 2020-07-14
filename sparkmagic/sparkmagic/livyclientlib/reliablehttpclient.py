# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
import json
from time import sleep
import requests
from requests_kerberos import HTTPKerberosAuth
from google.auth import compute_engine
import google.auth  

from google.auth.transport.requests import Request
import google.auth.transport.urllib3 
import urllib3 
from google.auth.transport.requests import AuthorizedSession
from google.auth.credentials import Credentials
from urllib.request import Request, urlopen, URLError

import subprocess
import google.auth.transport 
import google.auth.transport.requests

from .googleauth import HTTPGoogleAuth
import sparkmagic.utils.configuration as conf
from sparkmagic.utils.sparklogger import SparkLog
from sparkmagic.utils.constants import MAGICS_LOGGER_NAME
import sparkmagic.utils.constants as constants
from sparkmagic.livyclientlib.exceptions import HttpClientException
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException
from google.auth.exceptions import DefaultCredentialsError
import google.auth._cloud_sdk  as sdk
import sys
import logging 
from google.auth.transport.urllib3 import AuthorizedHttp




class ReliableHttpClient(object):
    """Http client that is reliable in its requests. Uses requests library."""

    def __init__(self, endpoint, headers, retry_policy):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logger = logging.getLogger('LOGGER_NAME')
        logger.info(headers)
        
        self._endpoint = endpoint
        self._headers = headers
        self._retry_policy = retry_policy
        if self._endpoint.auth == constants.AUTH_KERBEROS:
            self._auth = HTTPKerberosAuth(**conf.kerberos_auth_configuration())
           
        elif self._endpoint.auth == constants.AUTH_ADC:
            """
            To use application default credentials we use default(), which takes two parameters, scopes and 
            request (google.auth.transport.Request). Google Application Default Credentials abstracts 
            authentication across the different Google Cloud Platform hosting environments. When running 
            on any Google Cloud hosting environment or when running locally with the Google Cloud SDK installed, 
            default() can automatically determine the credentials from the environment. More here: 
            https://github.com/googleapis/google-auth-library-python/blob/master/google/auth/_default.py
            
            But if credentials are not set up, then if the notebook is running on GCE, then run 'gcloud auth login'.
            This authenticates with a user identity (via web flow) which then authorizes gcloud and other SDK tools 
            to access Google Cloud Platform. If the notebook is running on GCE, then run 'gcloud auth application-default 
            login'. This authenticates with a user identity (via a web flow) but uses the credentials as a proxy for a 
            service account. 
            
            **How do I know, if credentials are not set up, whether it is run on GCE or not. I check this from 
            within the code: https://cloud.google.com/compute/docs/storing-retrieving-metadata#querying
            """

            credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            
            
            Credentials.apply(credentials, headers, token=sdk.get_auth_access_token())
            logger.info(sdk.get_application_default_credentials_path())
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            req =  HTTPGoogleAuth(sdk.get_auth_access_token())
            logger.info(req)
            self._auth = HTTPGoogleAuth(sdk.get_auth_access_token())
            
            if self.get_project_id()!= '': 
                bashCommand = "gcloud auth application-default login"
                output = subprocess.check_output(['bash','-c', bashCommand])
                logger.info('GCE')
                
            else: 
                bashCommand = "gcloud auth login"
                output = subprocess.check_output(['bash','-c', bashCommand])
                logger.info('local')

            

            #if notebook is running locally / on premise
            
            #authed_session = AuthorizedSession(credentials)
            

            #self._auth = credentials
            """
            try: 
                credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            except DefaultCredentialsError: 
               
                #if notebook is running on GCE
                if self.get_project_id()!= '': 
                    bashCommand = "gcloud auth application-default login"
                    output = subprocess.check_output(['bash','-c', bashCommand])
                #if notebook is running locally / on premise
                else:
                    bashCommand = "gcloud auth login"
                    output = subprocess.check_output(['bash','-c', bashCommand])
                credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            #so now we have credentials, but we need to attach this to request header object (cause thats what HTTPKerberosAuth does)
            #so first we get Requests request adapter (request object), then we can attach our credentials (token) to this request header
            # https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html 
            request = google.auth.transport.requests.Request()
            #Credentials.apply(credentials, request)
            self._auth = credentials.refresh(request)
            #Could also set self._auth = AuthorizedSession(credentials) but going to see if the other way works first. 
            # https://google-auth.readthedocs.io/en/latest/user-guide.html#requests 
            """
        elif self._endpoint.auth == constants.AUTH_BASIC:
            self._auth = (self._endpoint.username, self._endpoint.password)
        elif self._endpoint.auth != constants.NO_AUTH:
            raise BadUserConfigurationException(u"Unsupported auth %s" %self._endpoint.auth)
        self._session = requests.Session()

        self.logger = SparkLog(u"ReliableHttpClient")

        self.verify_ssl = not conf.ignore_ssl_errors()
        if not self.verify_ssl:
            self.logger.debug(u"ATTENTION: Will ignore SSL errors. This might render you vulnerable to attacks.")
            requests.packages.urllib3.disable_warnings()

    def get_project_id(self):
        headers = {'Metadata-Flavor': 'Google'}
        project_id_request = requests.get('http://metadata.google.internal/computeMetadata/v1/project/project-id',headers )
        logger = logging.getLogger('LOGGER_NAME')
        logger.basicConfig(stream=sys.stdout, level=logging.INFO)
        try:
            with urlopen(project_id_request) as response:
                value = response.read().decode()
                logger.info(value)
                return value
        except Exception:       
            logger.info("not running on GCE")
        return ''

    def get_headers(self):
        return self._headers

    def compose_url(self, relative_url):
        r_u = "/{}".format(relative_url.rstrip(u"/").lstrip(u"/"))
        return self._endpoint.url + r_u

    def get(self, relative_url, accepted_status_codes):
        """Sends a get request. Returns a response."""
        return self._send_request(relative_url, accepted_status_codes, self._session.get)

    def post(self, relative_url, accepted_status_codes, data):
        """Sends a post request. Returns a response."""
        return self._send_request(relative_url, accepted_status_codes, self._session.post, data)

    def delete(self, relative_url, accepted_status_codes):
        """Sends a delete request. Returns a response."""
        return self._send_request(relative_url, accepted_status_codes, self._session.delete)

    def _send_request(self, relative_url, accepted_status_codes, function, data=None):
        return self._send_request_helper(self.compose_url(relative_url), accepted_status_codes, function, data, 0)

    def _send_request_helper(self, url, accepted_status_codes, function, data, retry_count):
        while True:
            try:
                if self._endpoint.auth == constants.NO_AUTH:
                    if data is None:
                        r = function(url, headers=self._headers, verify=self.verify_ssl)
                    else:
                        r = function(url, headers=self._headers, data=json.dumps(data), verify=self.verify_ssl)
                else:
                    if data is None:
                        r = function(url, headers=self._headers, auth=self._auth, verify=self.verify_ssl)
                    else:
                        r = function(url, headers=self._headers, auth=self._auth,
                                     data=json.dumps(data), verify=self.verify_ssl)
            except requests.exceptions.RequestException as e:
                error = True
                r = None
                status = None
                text = None

                self.logger.error(u"Request to '{}' failed with '{}'".format(url, e))
            else:
                error = False
                status = r.status_code
                text = r.text

            if error or status not in accepted_status_codes:
                if self._retry_policy.should_retry(status, error, retry_count):
                    sleep(self._retry_policy.seconds_to_sleep(retry_count))
                    retry_count += 1
                    continue

                if error:
                    raise HttpClientException(u"Error sending http request and maximum retry encountered.")
                else:
                    raise HttpClientException(u"Invalid status code '{}' from {} with error payload: {}"
                                              .format(status, url, text))
            return r
