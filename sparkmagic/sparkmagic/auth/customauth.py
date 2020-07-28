
import sparkmagic.utils.configuration as conf
from tornado import web
from hdijupyterutils.ipythondisplay import IpythonDisplay
from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory


#class Authenticator(AuthBase):

class Authenticator(object):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
    #Name of the login service that this authenticator is providing using to authenticate users. 
    # Example: Google. Setting this value replaces the manage_spark widget auth dropdown / setting dropdown sets this???
    #must be set to one of self.auth.constants? or sets constant
        #self.login_service = u"None"
        #self.widgets
        self.login_service = u"None"
        self.url = 'http://example.com/livy'
        self.get_widgets()
    # pretty sure don't need addresss to show, but would need additional fields like for basic user name and password to show. 
        


    def get_widgets(self): 
        ipywidget_factory = IpyWidgetFactory()
        
        self.address_widget = ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width="800px"
        )

        self.url = self.address_widget.value

      
        widgets = {self.address_widget}

       
        return widgets #self.widgets

    def url(self): 
       
        return self.url

    def show_correct_endpoint_fields(self): 
        self.address_widget.layout.display = 'flex'
    #def get_widgets(self): 

    def hide_correct_endpoint_fields(self): 
        self.address_widget.layout.display = 'none'
    #def get_widgets(self): 
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
        if self.login_service == u"None": 
            return {
                u"login_service": self.login_service, 
                u"request": None
            }
        else: 
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


   
