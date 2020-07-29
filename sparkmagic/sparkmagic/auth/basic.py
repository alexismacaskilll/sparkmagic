
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
from requests.auth import HTTPBasicAuth
from .customauth import Authenticator


class Basic(HTTPBasicAuth, Authenticator):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
        Authenticator.__init__(self)
        #Name of the login service that this authenticator is providing using to authenticate users. 
        #self.login_service = u"Basic"
        self.username = 'username'
        self.password = 'password'
    
    def get_widgets(self, widget_width): 
        Authenticator.get_widgets(self, widget_width)
        ipywidget_factory = IpyWidgetFactory()

        self.user_widget = ipywidget_factory.get_text(
            description='Username:',
            value='username',
            width=widget_width
        )
       
        self.password_widget = ipywidget_factory.get_text(
            description='Password:',
            value='password',
            width=widget_width
        )
        
        widgets = {self.address_widget, self.user_widget, self.password_widget}
        return widgets 

    def update_with_widget_values(self):
        Authenticator.update_with_widget_values(self)
        self.username = self.user_widget.value
        self.password = self.password_widget.value

    def __call__(self, request):
        HTTPBasicAuth.__call__(request)
        
    # can I add username / password to hash? 
    # had to add this because otherwise self.authWidgets[instance].add(widget) in addendpointwidget.py errors
    # saying 'Basic' is not hashable
    def __hash__(self):
        return hash((self.url, self.login_service))



   
