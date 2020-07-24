﻿
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory


#class Authenticator(AuthBase):
class Authenticator(object):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self, login_service = u"None", widgets = None, url = None):
    #Name of the login service that this authenticator is providing using to authenticate users. 
    # Example: Google. Setting this value replaces the manage_spark widget auth dropdown / setting dropdown sets this???
    #must be set to one of self.auth.constants? or sets constant
        #self.login_service = u"None"
        #self.widgets
        self.get_widgets()

    # pretty sure don't need addresss to show, but would need additional fields like for basic user name and password to show. 
        

        
        self.cluster_name_widget = self.ipywidget_factory.get_text(
            description='Cluster:',
            value='amacaskill-livy',
            width=widget_width
        )



    def get_widgets(self): 
        ipywidget_factory = IpyWidgetFactory()
        
        self.address_widget = self.ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width=widget_width
        )

        self.url = self.address_widget.value

      
        self.widgets = self.widgets.append(self.address_widget)

        self.url = self.address_widget.value
        return self.widgets

    def url(self): 
        self.url = self.address_widget.value
        return self.address_widget.value

    def show_correct_endpoint_fields(self): 
        self.address.widget.layout.display = 'flex'
    #def get_widgets(self): 

    def authenticate(self, handler, data):
        
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
        

    def get_authenticated_user(self, handler, data):
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
                u"login_service": self.login_service
            }
        authenticated =  self.authenticate(handler, data)
        if authenticated is None:
            return None #maybe some error that auth failed. 
        if 'login_service' not in authenticated:
            raise ValueError("user missing a login service: %r" % authenticated)
        return authenticated


    def HTTP_Auth(self, handler, data):

        """
        When an authentication handler is attached to a request, it is called during 
        request setup. The __call__ method must therefore do whatever is required 
        to make the authentication work. Some forms of authentication will 
        additionally add hooks to provide further functionality.
        """
        return None

        #if self.login_service == u"None": 

        """Authenticate the user who is attempting to log in
        Returns user dict if successful, None otherwise.
        This calls `authenticate`, which should be overridden in subclasses.
        This is the outer API for authenticating a user.
        Subclasses should not override this method.
        The various stages can be overridden separately:
         - `authenticate` turns formdata into a username
"""
        


    #get_handlers? 
    #login / login url 
    #def refresh_user(self, user, handler=None)?


   