
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory

from requests_kerberos import HTTPKerberosAuth
from .customauth import Authenticator


class Kerberos(HTTPKerberosAuth, Authenticator):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
        super().__init__(self)
        #Name of the login service that this authenticator is providing using to authenticate users. 
        self.login_service = u"Kerberos"
        self.url = 'http://example.com/livy'
        
    def get_widgets(self, widget_width): 
        basic_widgets = super().get_widgets(widget_width)
        ipywidget_factory = IpyWidgetFactory()
        
        self.address_widget = ipywidget_factory.get_text(
            description='Adbhkbdress:',
            value='http://example.com/livy',
            width=widget_width
        )

        basic_widgets.add(self.address_widget)

        return basic_widgets 

    def update_with_widget_values(self): 
        self.url = self.address_widget.value
       
   
    def __call__(self, request):
        super().__call__(request)
        
    # had to add this because otherwise self.authWidgets[instance].add(widget) in addendpointwidget.py errors
    # saying 'Basic' is not hashable
    def __hash__(self):
        return hash((self.url, self.login_service))
    
    




   
