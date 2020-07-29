﻿
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory

class Authenticator(object):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
        self.login_service = u"None"
        self.url = 'http://example.com/livy'
    

    def get_widgets(self, widget_width): 
        ipywidget_factory = IpyWidgetFactory()
        
        self.address_widget = ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width="800px"
        )
        widgets = {self.address_widget}
        return widgets 

    def update_with_widget_values(self): 
        self.url = self.address_widget.value
        

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
        return None
       
        
    
    def get_authenticated_user(self):
        """Authenticate the user who is attempting to log in
        Returns user dict if successful, None otherwise.
        This calls `authenticate`, which should be overridden in subclasses.
        This is the outer API for authenticating a user.
        Subclasses should not override this method.
        The various stages can be overridden separately:
         - `authenticate` turns formdata into a username

        removed: 
         - normalize_username` normalizes the username
         - `check_whitelist` checks against the user whitelist

        """
        if self.login_service == u"None": 
            return {
                u"login_service": self.login_service, 
                u"request": None
            }
        authenticated =  self.authenticate()
        """
        if authenticated is None:
            return None #maybe some error that auth failed. 
        if 'login_service' not in authenticated:
            raise ValueError("user missing a login service: %r" % authenticated)
        """
        return authenticated


    
        


    #get_handlers? 
    #login / login url 
    #def refresh_user(self, user, handler=None)?


   
