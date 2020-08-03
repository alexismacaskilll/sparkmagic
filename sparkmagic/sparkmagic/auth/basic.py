from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
from requests.auth import HTTPBasicAuth
from .customauth import Authenticator
from sparkmagic.utils.constants import WIDGET_WIDTH


class Basic(HTTPBasicAuth, Authenticator):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
        #Authenticator.__init__(self, widget_width)
        self.username = 'username'
        self.password = 'password'
        HTTPBasicAuth.__init__(self, self.username, self.password)
        
        self.widgets = self.get_widgets(WIDGET_WIDTH)
    
    def get_widgets(self, widget_width): 
        ipywidget_factory = IpyWidgetFactory()

        self.user_widget = ipywidget_factory.get_text(
            description='Username:',
            value=self.username,
            width=widget_width
        )
       
        self.password_widget = ipywidget_factory.get_text(
            description='Password:',
            value=self.password,
            width=widget_width
        )
        
        widgets = [self.user_widget, self.password_widget]
        return Authenticator.get_widgets(self) + widgets

    def update_with_widget_values(self):
        Authenticator.update_with_widget_values(self)
        self.username = self.user_widget.value
        self.password = self.password_widget.value

    def __call__(self, request):
        return HTTPBasicAuth.__call__(self, request)
        
    def __hash__(self):
        return id(self)