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
        return r


   
        
    