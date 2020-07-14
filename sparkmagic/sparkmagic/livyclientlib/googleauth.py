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

from requests.auth import AuthBase
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



class HTTPGoogleAuth(AuthBase):
    """Attaches HTTP Google Auth Authentication to the given Request
    object."""

    def __init__(self, token = None):
        self.token = token
    
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {}'.format(self.token)
        r.register_hook('response', self.handle_response)
        return r

    

    def handle_response(self, response):
        """Handles all responses with the exception of 401s.

        This is necessary so that we can authenticate responses if requested"""

        
        """
        if self.mutual_authentication in (REQUIRED, OPTIONAL) and not self.auth_done:

            is_http_error = response.status_code >= 400

            if _negotiate_value(response) is not None:
                log.debug("handle_other(): Authenticating the server")
                if not self.authenticate_server(response):
                    # Mutual authentication failure when mutual auth is wanted,
                    # raise an exception so the user doesn't use an untrusted
                    # response.
                    log.error("handle_other(): Mutual authentication failed")
                    raise MutualAuthenticationError("Unable to authenticate "
                                                    "{0}".format(response))

                # Authentication successful
                log.debug("handle_other(): returning {0}".format(response))
                self.auth_done = True
                return response

            elif is_http_error or self.mutual_authentication == OPTIONAL:
                if not response.ok:
                    log.error("handle_other(): Mutual authentication unavailable "
                              "on {0} response".format(response.status_code))

                if(self.mutual_authentication == REQUIRED and
                       self.sanitize_mutual_error_response):
                    return SanitizedResponse(response)
                else:
                    return response
            else:
                # Unable to attempt mutual authentication when mutual auth is
                # required, raise an exception so the user doesn't use an
                # untrusted response.
                log.error("handle_other(): Mutual authentication failed")
                raise MutualAuthenticationError("Unable to authenticate "
                                                "{0}".format(response))
        else:
            log.debug("handle_other(): returning {0}".format(response))
            return response
   
        """
        return response
    