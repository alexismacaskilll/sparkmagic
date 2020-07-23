

from tornado import web


#class Authenticator(AuthBase):
class Authenticator(object):
    """Base class for implementing an authentication provider for SparkMagic"""
    
    #Name of the login service that this authenticator is providing using to authenticate users. 
    # Example: Google. Setting this value replaces the manage_spark widget auth dropdown / setting dropdown sets this???
    #must be set to one of self.auth.constants? or sets constant
    login_service = 'override in subclass'
    
    enable_custom_endpoint_widget = False

    def authenticate(self, handler, data):
        """Authenticate a user with login form data
        It must return the username on successful authentication,
        and return None on failed authentication.
        
        Args:
            handler (tornado.web.RequestHandler): the current request handler
            data (dict): The formdata of the login form.
                         The default form has 'username' and 'password' fields.
        Returns:
            user (str or dict or None):
                The username of the authenticated user,
                or None if Authentication failed.
                The Authenticator may return a dict instead, which MUST have a
                key `name` holding the username, and MAY have two optional keys
                set: `auth_state`, a dictionary of of auth state that will be
                persisted; and `admin`, the admin setting value for the user.
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
        authenticated =  self.authenticate(handler, data)
        if authenticated is None:
            return None #maybe some error that auth failed. 
        if 'name' not in authenticated:
            raise ValueError("user missing a name: %r" % authenticated)

        return authenticated

    def _show_correct_endpoint_fields(self):


    #get_handlers? 
    #login / login url 
    #def refresh_user(self, user, handler=None)?


   
