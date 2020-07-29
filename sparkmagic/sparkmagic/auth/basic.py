
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
from requests.auth import HTTPBasicAuth
from .customauth import Authenticator


#class Authenticator(AuthBase):

class Basic(  HTTPBasicAuth):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
        #Name of the login service that this authenticator is providing using to authenticate users. 
        self.login_service = u"Basic"
        self.url = 'http://example.com/livy'
        


    def get_widgets(self, widget_width): 
        ipywidget_factory = IpyWidgetFactory()
        
        self.address_widget = ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width=widget_width
        )

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
        self.url = self.address_widget.value
        self.username = self.user_widget.value
        self.password = self.password_widget.value

    def authenticate(self):
        
        """Authenticate a user with login form data
        It must return dict on successful authentication,
        and return None on failed authentication. self.login_service
        is not none, must override this in subclass
        
        Args:
            handler (tornado.web.RequestHandler): the current request handler
            data (dict): The formdata of the login form.
                         The default form has 'username' and 'password' fields.
        Returns:
            user (dict or None):
                The Authenticator may return a dict instead, which MUST have a
                key `login_service` holding the login_service, and other optional 
                keys the auth_type requires like tokens for google auth, user names / 
                passwords. 
        """
        

    def __call__(self, request):
        super().__call__(request)
        
    # can I add username / password to hash? 
    # had to add this because otherwise self.authWidgets[instance].add(widget) in addendpointwidget.py errors
    # saying 'Basic' is not hashable
    def __hash__(self):
        return hash((self.url, self.login_service))
    




   
