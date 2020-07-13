# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
import json
from time import sleep
import requests
from requests_kerberos import HTTPKerberosAuth
from google.auth import compute_engine
import google.auth  
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials

import sparkmagic.utils.configuration as conf
from sparkmagic.utils.sparklogger import SparkLog
from sparkmagic.utils.constants import MAGICS_LOGGER_NAME
import sparkmagic.utils.constants as constants
from sparkmagic.livyclientlib.exceptions import HttpClientException
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException
from google.auth.exceptions import DefaultCredentialsError


class ReliableHttpClient(object):
    """Http client that is reliable in its requests. Uses requests library."""

    def __init__(self, endpoint, headers, retry_policy):
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
            
            **How do I know, if credentials are not set up, whether it is run on GCE or not. How can I check this from 
            within the code. 
            """
          
            
            try: 
                credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            except DefaultCredentialsError: 
                import subprocess
                #if notebook is running on GCE then we do this: 
                bashCommand = "gcloud auth application-default login"
                output = subprocess.check_output(['bash','-c', bashCommand])
                #if notebook is running locally / on premise, then we do this: 
                bashCommand = "gcloud auth login"
                output = subprocess.check_output(['bash','-c', bashCommand])
                credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            #so now we have credentials, but we need to attach this to request header object (cause thats what HTTPKerberosAuth does)
            #so first we get Requests request adapter (request object), then we can attach our credentials (token) to this request header
            # https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html 
            request = google.auth.transport.requests.Request()
            Credentials.apply(credentials, request)
            self._auth = credentials
            #Could also set self._auth = AuthorizedSession(credentials) but going to see if the other way works first. 
            # https://google-auth.readthedocs.io/en/latest/user-guide.html#requests 
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
