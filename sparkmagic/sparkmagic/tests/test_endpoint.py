from nose.tools import assert_equals, assert_not_equal, assert_false

from sparkmagic.livyclientlib.exceptions import BadUserDataException
from sparkmagic.livyclientlib.endpoint import Endpoint
from sparkmagic.auth.basic import Basic
from sparkmagic.auth.kerberos import Kerberos
from sparkmagic.utils.constants import WIDGET_WIDTH

def test_equality():
    basic_auth = Basic(WIDGET_WIDTH)
    kerberos_auth = Kerberos(WIDGET_WIDTH)
    assert_equals(Endpoint("http://url.com", basic_auth), Endpoint("http://url.com", basic_auth))
    assert_equals(Endpoint("http://url.com", kerberos_auth), Endpoint("http://url.com", kerberos_auth))

def test_inequality():
    basic_auth1 = Basic(WIDGET_WIDTH)
    basic_auth2 = Basic(WIDGET_WIDTH)
    assert_false(assert_equals(Endpoint("http://url.com", basic_auth1), Endpoint("http://url.com", basic_auth2)))
    kerberos_auth1 = Kerberos(WIDGET_WIDTH)
    kerberos_auth2 = Kerberos(WIDGET_WIDTH)
    assert_not_equal(Endpoint("http://url.com", kerberos_auth1), Endpoint("http://url.com", kerberos_auth2))

def test_invalid_url():
    basic_auth = Basic(WIDGET_WIDTH)
    try:
        endpoint = Endpoint(None, basic_auth)
        assert False
    except BadUserDataException:
        assert True

