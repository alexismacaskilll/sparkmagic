from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
import sparkmagic.utils.configuration as conf
from requests_kerberos import HTTPKerberosAuth
from .customauth import Authenticator
 

class Kerberos(HTTPKerberosAuth, Authenticator):
    #Base class for implementing an authentication provider for SparkMagic

    def __init__(self):
        HTTPKerberosAuth.__init__(self, **conf.kerberos_auth_configuration())
        Authenticator.__init__(self)
        
    def __call__(self, request):
        return HTTPKerberosAuth.__call__(self, request)

    # had to add this because otherwise self.authWidgets[instance].add(widget) in addendpointwidget.py errors
    # saying 'Kerberos' is not hashable
    def __hash__(self):
        return id(self)
    
    




   
