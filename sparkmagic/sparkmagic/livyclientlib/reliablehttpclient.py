﻿# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
import json
from time import sleep
import requests
from requests_kerberos import HTTPKerberosAuth

import sparkmagic.utils.configuration as conf
from sparkmagic.utils.sparklogger import SparkLog
from sparkmagic.utils.constants import MAGICS_LOGGER_NAME
import sparkmagic.utils.constants as constants
from sparkmagic.livyclientlib.exceptions import HttpClientException
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException
from sparkmagic.auth.customauth import Authenticator
import logging 






class ReliableHttpClient(object):
    """Http client that is reliable in its requests. Uses requests library."""

    def __init__(self, endpoint, headers, retry_policy):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logger = logging.getLogger('LOGGER_NAME')
        self._endpoint = endpoint
        self._headers = headers
        self._retry_policy = retry_policy
        #self.auth needs to be set to an HTTP Authentication type

        # we want to pass configuration if necessary, like Kerberos:
        # self._auth = HTTPKerberosAuth(**conf.kerberos_auth_configuration())
        # but we want to load this authomatically not hardcode. See
        # _get_default_endpoints() to see how to do it
        logger.info(self._endpoint.url)
        logger.info(self._endpoint.auth)

        result = self._endpoint.auth.get_authenticated_user()
        logger.info(result)
        json_formatted = json.loads(result)
        logger.info(json_formatted)

        login_service = str(json_formatted['login_service'])
        logger.info(login_service)
        auth_request = (json_formatted['login_service'])

        logger.info(auth_request)

        self._auth = auth_request

        #need to implement for Kerberos, and auth basic later. 
        # Also removing this check because auth is a dropdown, an auth type will always be set.     
        """
        elif self._endpoint.auth != constants.NO_AUTH:
            raise BadUserConfigurationException(u"Unsupported auth %s" %self._endpoint.auth)
        """
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
