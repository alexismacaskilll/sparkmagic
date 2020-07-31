from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
from requests.auth import HTTPBasicAuth
from .customauth import Authenticator


class Basic(HTTPBasicAuth, Authenticator):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self, widget_width):
        Authenticator.__init__(self, widget_width)
        #Name of the login service that this authenticator is providing using to authenticate users. 
        self.login_service = u"Basic"
        HTTPBasicAuth.__init__(self, 'username', 'password')
        self.widgets = self.get_widgets(widget_width)
    
    def get_widgets(self, widget_width): 
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
        
        widgets = {self.user_widget, self.password_widget}
        return widgets.union(Authenticator.get_widgets(self, widget_width))

    def update_with_widget_values(self):
        Authenticator.update_with_widget_values(self)
        self.username = self.user_widget.value
        self.password = self.password_widget.value

    def __call__(self, request):
        return HTTPBasicAuth.__call__(request)
        
    def __hash__(self):
        return hash((self.url, self.login_service))