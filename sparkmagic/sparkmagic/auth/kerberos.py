"""Class for implementing a Kerberos authenticator for SparkMagic"""

from requests_kerberos import HTTPKerberosAuth
import sparkmagic.utils.configuration as conf
from .customauth import Authenticator


class Kerberos(HTTPKerberosAuth, Authenticator):
    """Kerberos authenticator for SparkMagic"""

    def __init__(self):
        HTTPKerberosAuth.__init__(self, **conf.kerberos_auth_configuration())
        Authenticator.__init__(self)

    def __call__(self, request):
        return HTTPKerberosAuth.__call__(self, request)

    def __hash__(self):
        return id(self)
