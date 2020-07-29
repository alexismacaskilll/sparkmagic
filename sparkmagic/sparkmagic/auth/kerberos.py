from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory


import sparkmagic.utils.configuration as conf



from requests_kerberos import HTTPKerberosAuth
from .customauth import Authenticator


class Kerberos(HTTPKerberosAuth, Authenticator):
    #Base class for implementing an authentication provider for SparkMagic

    def __init__(self):
        Authenticator.__init__(self)
        #Name of the login service that this authenticator is providing using to authenticate users. 
        
    def __call__(self, request):
        HTTPKerberosAuth.__call__(request)
        
    # had to add this because otherwise self.authWidgets[instance].add(widget) in addendpointwidget.py errors
    # saying 'Kerberos' is not hashable
    def __hash__(self):
        return hash((self.url, self.login_service))
    
    




   
