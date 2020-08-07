# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
import json
from mock import patch, PropertyMock, MagicMock, sentinel, Mock
from nose.tools import raises, assert_equals, with_setup, assert_is_not_none, assert_false, assert_true
import requests
from requests_kerberos.kerberos_ import HTTPKerberosAuth, REQUIRED, OPTIONAL
from sparkmagic.auth.basic import Basic
from sparkmagic.auth.kerberos import Kerberos
import sparkmagic.auth.google as google_auth_class
import google.auth
from google.auth.exceptions import DefaultCredentialsError
import sparkmagic
from sparkmagic.auth.google import GoogleAuth
from sparkmagic.auth.customauth import Authenticator
from sparkmagic.livyclientlib.endpoint import Endpoint
from sparkmagic.livyclientlib.exceptions import HttpClientException
from sparkmagic.livyclientlib.exceptions import BadUserConfigurationException
from sparkmagic.livyclientlib.linearretrypolicy import LinearRetryPolicy
from sparkmagic.livyclientlib.reliablehttpclient import ReliableHttpClient
import sparkmagic.utils.configuration as conf
import sparkmagic.utils.constants as constants
from unittest.mock import create_autospec
from google.oauth2 import credentials
import os
import subprocess
import google

retry_policy = None
sequential_values = []
google_auth = GoogleAuth()
endpoint = Endpoint("http://url.com", google_auth)

def _setup():
    global retry_policy
    retry_policy = LinearRetryPolicy(0.01, 5)

def _teardown():
    pass

def return_sequential():
    global sequential_values
    val = sequential_values[0]
    sequential_values = sequential_values[1:]
    return val


@with_setup(_setup, _teardown)
def test_get():
    with patch('requests.Session.get') as patched_get:
        type(patched_get.return_value).status_code = 200
        client = ReliableHttpClient(endpoint, {}, retry_policy)

        result = client.get("r", [200])

        assert_equals(200, result.status_code)


@raises(HttpClientException)
@with_setup(_setup, _teardown)
def test_get_throws():
    with patch('requests.Session.get') as patched_get:
        type(patched_get.return_value).status_code = 500

        client = ReliableHttpClient(endpoint, {}, retry_policy)

        client.get("r", [200])


@with_setup(_setup, _teardown)
def test_get_will_retry():
    global sequential_values, retry_policy
    retry_policy = MagicMock()
    retry_policy.should_retry.return_value = True
    retry_policy.seconds_to_sleep.return_value = 0.01

    with patch('requests.Session.get') as patched_get:
        # When we call assert_equals in this unit test, the side_effect is executed.
        # So, the last status_code should be repeated.
        sequential_values = [500, 200, 200]
        pm = PropertyMock()
        pm.side_effect = return_sequential
        type(patched_get.return_value).status_code = pm
        client = ReliableHttpClient(endpoint, {}, retry_policy)

        result = client.get("r", [200])

        assert_equals(200, result.status_code)
        retry_policy.should_retry.assert_called_once_with(500, False, 0)
        retry_policy.seconds_to_sleep.assert_called_once_with(0)


@with_setup(_setup, _teardown)
def test_post():
    with patch('requests.Session.post') as patched_post:
        type(patched_post.return_value).status_code = 200

        client = ReliableHttpClient(endpoint, {}, retry_policy)

        result = client.post("r", [200], {})

        assert_equals(200, result.status_code)


@raises(HttpClientException)
@with_setup(_setup, _teardown)
def test_post_throws():
    with patch('requests.Session.post') as patched_post:
        type(patched_post.return_value).status_code = 500

        client = ReliableHttpClient(endpoint, {}, retry_policy)

        client.post("r", [200], {})


@with_setup(_setup, _teardown)
def test_post_will_retry():
    global sequential_values, retry_policy
    retry_policy = MagicMock()
    retry_policy.should_retry.return_value = True
    retry_policy.seconds_to_sleep.return_value = 0.01

    with patch('requests.Session.post') as patched_post:
        # When we call assert_equals in this unit test, the side_effect is executed.
        # So, the last status_code should be repeated.
        sequential_values = [500, 200, 200]
        pm = PropertyMock()
        pm.side_effect = return_sequential
        type(patched_post.return_value).status_code = pm
        client = ReliableHttpClient(endpoint, {}, retry_policy)

        result = client.post("r", [200], {})

        assert_equals(200, result.status_code)
        retry_policy.should_retry.assert_called_once_with(500, False, 0)
        retry_policy.seconds_to_sleep.assert_called_once_with(0)


@with_setup(_setup, _teardown)
def test_delete():
    with patch('requests.Session.delete') as patched_delete:
        type(patched_delete.return_value).status_code = 200

        client = ReliableHttpClient(endpoint, {}, retry_policy)

        result = client.delete("r", [200])

        assert_equals(200, result.status_code)

@raises(HttpClientException)
@with_setup(_setup, _teardown)
def test_delete_throws():
    with patch('requests.Session.delete') as patched_delete:
        type(patched_delete.return_value).status_code = 500

        client = ReliableHttpClient(endpoint, {}, retry_policy)

        client.delete("r", [200])


@with_setup(_setup, _teardown)
def test_delete_will_retry():
    global sequential_values, retry_policy
    retry_policy = MagicMock()
    retry_policy.should_retry.return_value = True
    retry_policy.seconds_to_sleep.return_value = 0.01

    with patch('requests.Session.delete') as patched_delete:
        # When we call assert_equals in this unit test, the side_effect is executed.
        # So, the last status_code should be repeated.
        sequential_values = [500, 200, 200]
        pm = PropertyMock()
        pm.side_effect = return_sequential
        type(patched_delete.return_value).status_code = pm
        client = ReliableHttpClient(endpoint, {}, retry_policy)

        result = client.delete("r", [200])

        assert_equals(200, result.status_code)
        retry_policy.should_retry.assert_called_once_with(500, False, 0)
        retry_policy.seconds_to_sleep.assert_called_once_with(0)


@with_setup(_setup, _teardown)
def test_will_retry_error_no():
    global sequential_values, retry_policy
    retry_policy = MagicMock()
    retry_policy.should_retry.return_value = False
    retry_policy.seconds_to_sleep.return_value = 0.01

    with patch('requests.Session.get') as patched_get:
        patched_get.side_effect = requests.exceptions.ConnectionError()
        client = ReliableHttpClient(endpoint, {}, retry_policy)

        try:
            client.get("r", [200])
            assert False
        except HttpClientException:
            retry_policy.should_retry.assert_called_once_with(None, True, 0)


@with_setup(_setup, _teardown)
def test_google_auth():
    endpoint = Endpoint("http://url.com", google_auth)
    client = ReliableHttpClient(endpoint, {}, retry_policy)
    assert_is_not_none(client._auth)
    assert isinstance(client._auth, GoogleAuth)
    assert hasattr(client._auth, 'url')
    assert hasattr(client._auth, 'widgets')
    
MOCK_GOOGLE = Mock(spec=GoogleAuth)
MOCK_CREDENTIALS = Mock(spec = credentials.Credentials)
def make_credentials():
    return credentials.Credentials(
        token=None,
        refresh_token='refresh',
        token_uri='token_uri',
        client_id='client_id',
        client_secret='client_secret',
    )
creds = make_credentials()
def test_default_credentials_configured_credentials_is_not_none():
    with patch('google.auth.default', return_value=(creds, 'project'), \
    autospec=True):
        assert_equals(GoogleAuth().credentials, creds)
        assert_is_not_none(GoogleAuth().credentials)

def test_default_credentials_not_configured_credentials_is_none():
    with patch('google.auth.default', side_effect=DefaultCredentialsError, \
    autospec=True):
        assert_equals(GoogleAuth().credentials, None)

def test_default_credentials_not_configured_account_pairs_contains_no_default():
    """Tests default-credentials is not in google credentials dropdown if if default credentials
    are not configured""" 
    with patch('google.auth.default', side_effect=DefaultCredentialsError, \
    autospec=True):
        assert_false('default-credentials' in GoogleAuth().google_credentials_widget.options)

def test_default_credentials_configured_account_pairs_contains_default():
    """Tests default-credentials is in google credentials dropdown if if default credentials
    are configured""" 
    with patch('google.auth.default', return_value=(MOCK_CREDENTIALS, 'project'), \
    autospec=True):
        assert_true('default-credentials' in GoogleAuth().google_credentials_widget.options)

#MOCK_CREDENTIALS = Mock(spec = credentials.Credentials)
auth_list = '[{"account": "account@google.com","status": "ACTIVE"}]'
def test_active_account_returns_valid_active_account_subprocess():
    with patch('subprocess.check_output', return_value = auth_list), \
        patch('google.auth.default', side_effect=DefaultCredentialsError), \
        patch('google.auth._cloud_sdk', return_value='token'):
        #assertion error: None != account@google.com
        credentialed_acccounts = sparkmagic.auth.google.list_credentialed_accounts()
        assert_equals(sparkmagic.auth.google.list_active_account(credentialed_acccounts), 'account@google.com')


def test_list_credentialed_accounts_subprocess():
    with patch('subprocess.check_output', return_value = auth_list), \
        patch('google.auth.default', side_effect=DefaultCredentialsError), \
        patch('google.auth._cloud_sdk', return_value='token'):
        #assertion error: None != account@google.com
        assert_equals(GoogleAuth().credentialed_accounts, ['account@google.com'])


def test_initialize_credentials_with_default_credentials():
    with patch('google.auth.default', return_value=(MOCK_CREDENTIALS, 'project'), \
    autospec=True):
        google_auth = GoogleAuth()
        assert_false(hasattr(google_auth.credentials, 'token'))
        assert_true(hasattr(google_auth.credentials, 'quota_project_id'))
        #this calls refresh which will error. 
        #request = mock.create_autospec(transport.Request)
        google_auth.initialize_credentials_with_auth_account_selection('default-credentials')
        #false is not true. Side effect to make refresh change correct. 
        #assert_true(hasattr(google_auth.credentials, 'token'))
        assert_true(hasattr(google_auth.credentials, 'quota_project_id'))

#DATA_DIR = os.path.join(os.path.dirname(__file__), ".", "data")
#AUTH_USER_JSON_FILE = os.path.join(DATA_DIR, "authorized_user_cloud_sdk.json")

with open(AUTH_USER_JSON_FILE, "r") as fh:
    AUTH_USER_INFO = json.load(fh)
with open('./data/authorized_user_cloud_sdk.json') as f: 
    USER_CREDENTIALS_JSON = json.load(f)
def test_initialize_credentials_with_user_credentals(): 
    with patch('google.auth.default', return_value=(MOCK_CREDENTIALS, 'project'), \
    autospec=True), patch('subprocess.check_output', return_value=USER_CREDENTIALS_JSON):
        google_auth = GoogleAuth()
        assert_false(hasattr(google_auth.credentials, 'token'))
        #this calls refresh which will error. 
        #request = mock.create_autospec(transport.Request)
        google_auth.initialize_credentials_with_auth_account_selection('account@google.com')
        #false is not true. Side effect to make refresh change correct. 
        #assert_true(hasattr(google_auth.credentials, 'token'))
        assert_false(hasattr(google_auth.credentials, 'quota_project_id'))


"""

def test_active_account_returns_valid_active_account():
    with patch('sparkmagic.auth.google.list_active_account') as list_active_account, \
        patch('sparkmagic.auth.google.list_accounts_pairs') as list_accounts_pairs:
        list_active_account.return_value = 'account@google.com'
        list_accounts_pairs.return_value = {'account@google.com':'account@google.com'}
        google_auth = GoogleAuth()  
        assert_equals('account@google.com', google_auth.active_account)

def test_active_account_returns_none_if_no_accounts():
    with patch('sparkmagic.auth.google.list_active_account') as list_active_account, \
        patch('sparkmagic.auth.google.list_accounts_pairs') as list_accounts_pairs, \
        patch('sparkmagic.auth.google.application_default_credentials_configured') as default_credentials_patch:
        default_credentials_patch.return_value = False
        list_accounts_pairs.return_value = {}
        list_active_account.return_value = None
        google_auth = GoogleAuth()
        assert_equals(None, google_auth.active_account)


def test_active_account_returns_none_if_no_accounts1():
    mock_credentials = Mock(spec=GoogleAuth)
    mock_credentials.return_value = Mock()
    mock_credentials_instance = mock_credentials.return_value
    mock_credentials_instance.application_default_credentials_configured.side_effect = \
        False
    mock_credentials_instance.list_active_account.side_effect = None
    assert_equals(mock_credentials_instance.list_active_account, None)
    #with patch('sparkmagic.auth.google.list_active_account') as list_active_account, \
     #   patch('sparkmagic.auth.google.list_accounts_pairs') as list_accounts_pairs:# , \
        #patch('google.auth.default') as default_credentials_patch:
        #default_credentials_patch.return_value = False
        #list_accounts_pairs.return_value = {}
        #list_active_account.return_value = None
        #google_auth = GoogleAuth()
"""





"""
def test_credentials_is_none_application_default_credentials_not_configured():
    with patch('google.auth.default') as default_credentials_patch:
    #with patch('sparkmagic.auth.google.application_default_credentials_configured') as default_credentials_patch:
        creds = credentials.Credentials(
            token=None,
            refresh_token='refresh',
            token_uri='http://token_uri',
            client_id='client_id',
            client_secret='client_secret',
        )
        default_credentials_patch.return_value = creds, 'project'
        #default_credentials_patch.return_value = False
        google_auth = GoogleAuth()
        google_auth.google_credentials_widget.value = 'default-credentials'
        google_auth.initialize_credentials_with_auth_account_selection()
        assert_equals(creds, google_auth.credentials)


def test_credentials_application_default_credentials_configured():
    with patch('sparkmagic.auth.google.application_default_credentials_configured') as default_credentials_patch:
        default_credentials_patch.return_value = True
        google_auth = GoogleAuth()
        isinstance(google_auth.credentials, credentials.Credentials)


"""


"""
def test_no_default_configured():
    with patch('sparkmagic.auth.google.GoogleAuth') as google_mock, \
        patch('google.auth.default') as default_credentials_patch: 
         instance = google_mock.return_value
         default_credentials_patch.return_value = DefaultCredentialsError
         assert_equals(instance.credentials, None )

    #with patch('google.auth.default', return_value=(MOCK_CREDENTIALS, 'project'), 
    #    autospec=True) as default_credentials_patch:
        #mock_credentials = Mock(spec=GoogleAuth)
        #mock_credentials.return_value = mock.Mock()
        #mock_credentials_instance = mock_credentials.return_value


        #default_credentials_patch.return_value = DefaultCredentialsError
      #  assert_equals(GoogleAuth().credentials, MOCK_CREDENTIALS )

        #google_auth1 = GoogleAuth()
        #assert None == google_auth1.credentials 

    #assert excinfo.match(r"not found")
"""
"""
def test_credentials_application_default_credentials_configured():
    with patch('sparkmagic.auth.google.application_default_credentials_configured') as default_credentials_patch, \
        patch('sparkmagic.auth.google.get_credentials_for_account') as get_cred_for_account_patch, \
        patch.object(GoogleAuth, 'google_credentials_widget', sentinel.google_credentials_widget):
        mock_credentials = Mock(spec=GoogleAuth)
        mock_credentials.google_credentials_widget.value = 'default-credentials'
        #trying to check that get_credentials_for_account() will call application default

"""      
"""       
def test_credentials_application_default_credentials_configured():
    with patch('sparkmagic.auth.google.application_default_credentials_configured') as default_credentials_configured_patch, \
        patch('google.auth.default') as default_credentials_patch:
        mock_credentials = Mock(spec=credentials.Credentials)
        mock_credentials.return_value = Mock()
        mock_credentials_instance = mock_credentials.return_value
        mock_credentials_instance.token = None
        #self.mock_credentials_instance.expiry = datetime.datetime(1980, 1, 1, 12)
        creds = credentials.Credentials(
            token=None,
            refresh_token='refresh',
            token_uri='token_uri',
            client_id='client_id',
            client_secret='client_secret',
        )

       
        #default_credentials_patch.return_value = creds 
        #default_credentials_configured_patch.return_value = True
        google_auth = GoogleAuth()

        #assert_equals(None, mock_credentials.credentials.token())
        isinstance(credentials.Credentials, google_auth.credentials)
        #assert_equals('refresh', google_auth.credentials.token())
        #assert_equals('token_uri', google_auth.credentials.token_uri())
        #assert_equals('client_secret', google_auth.credentials.client_secret())

"""
"""
def test_credentials_application_default_credentials_configured():
    with patch('sparkmagic.auth.google.application_default_credentials_configured') as default_credentials_configured_patch, \
        patch('google.auth.default') as default_credentials_patch:
        creds = credentials.Credentials(
            token=None,
            refresh_token='refresh',
            token_uri='token_uri',
            client_id='client_id',
            client_secret='client_secret',
        )
       
        default_credentials_patch.return_value = creds 
        default_credentials_configured_patch.return_value = True
        google_auth = GoogleAuth()

        assert_equals(None, google_auth.credentials.token())
        isinstance(credentials.Credentials, google_auth.credentials)
        #assert_equals('refresh', google_auth.credentials.token())
        #assert_equals('token_uri', google_auth.credentials.token_uri())
        #assert_equals('client_secret', google_auth.credentials.client_secret())


def test_default_state():
    
    creds = credentials.Credentials(
                token=None,
                refresh_token='refresh',
                token_uri='token_uri',
                client_id='client_id',
                client_secret='client_secret',
            )
    assert not creds.valid
    # Expiration hasn't been set yet
    assert not creds.expired
    # Scopes aren't required for these credentials

@classmethod
def make_credentials(cls):
    return credentials.Credentials(
        token=None,
        refresh_token=cls.REFRESH_TOKEN,
        token_uri=cls.TOKEN_URI,
        client_id=cls.CLIENT_ID,
        client_secret=cls.CLIENT_SECRET,
    )


 
def test_default_state():
    
    creds = credentials.Credentials(
                token="token",
                refresh_token=self.REFRESH_TOKEN,
                token_uri=self.TOKEN_URI,
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
            )
    assert not credentials.valid
    # Expiration hasn't been set yet
    assert not credentials.expired
    # Scopes aren't required for these credentials



def test_from_authorized_user_info():
        info = AUTH_USER_INFO.copy()
        google.get_credentials_for_account

        creds = credentials.Credentials.from_authorized_user_info(info)
        assert creds.client_secret == info["client_secret"]
        assert creds.client_id == info["client_id"]
        assert creds.refresh_token == info["refresh_token"]
        assert creds.token_uri == credentials._GOOGLE_OAUTH2_TOKEN_ENDPOINT
        assert creds.scopes is None

        scopes = ["email", "profile"]
        creds = credentials.Credentials.from_authorized_user_info(info, scopes)
        assert creds.client_secret == info["client_secret"]
        assert creds.client_id == info["client_id"]
        assert creds.refresh_token == info["refresh_token"]
        assert creds.token_uri == credentials._GOOGLE_OAUTH2_TOKEN_ENDPOINT
        assert creds.scopes == scopes


def test_default_state_no_gcloud():
    if (sparkmagic.)
    credentials = google_auth.credentials
    assert not credentials.valid
    # Expiration hasn't been set yet
    assert not credentials.expired
    # Scopes aren't required for these credentials
    assert credentials.requires_scopes
    # Test properties

    assert credentials.refresh_token == self.REFRESH_TOKEN
    assert credentials.token_uri == self.TOKEN_URI
    assert credentials.client_id == self.CLIENT_ID
    assert credentials.client_secret == self.CLIENT_SECRET
  


def test_default_credentials():
    with patch("google.auth.default", autospec=True) as default:
        default.return_value = (sentinel.credentials)

        credentials = google.auth.default()

        assert_equals(credentials, sentinel.credentials)


def test_default_credentials_oauth2():
        default_patch = patch(
            "oauth2client.client.GoogleCredentials.get_application_default"
        )

        with default_patch as default:
            default.return_value = sentinel.credentials

            credentials = google.auth.default()

            self.assertEqual(credentials, sentinel.credentials)


"""
