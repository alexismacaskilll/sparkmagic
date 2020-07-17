# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
from sparkmagic.controllerwidget.abstractmenuwidget import AbstractMenuWidget
from sparkmagic.livyclientlib.endpoint import Endpoint
import sparkmagic.utils.constants as constants
import sparkmagic.livyclientlib.googleauth as GoogleAuth
from sparkmagic.livyclientlib.exceptions import GcloudNotInstalledException, BadUserConfigurationException, BadUserDataException
from google.auth.exceptions import UserAccessTokenError
from sparkmagic.livyclientlib.livysession import LivySession
from hdijupyterutils.ipythondisplay import IpythonDisplay


ipython_display_new = IpythonDisplay()
        
class AddEndpointWidget(AbstractMenuWidget):

    def __init__(self, spark_controller, ipywidget_factory, ipython_display, endpoints, endpoints_dropdown_widget,
                 refresh_method):
        # This is nested
        super(AddEndpointWidget, self).__init__(spark_controller, ipywidget_factory, ipython_display, True)

        widget_width = "800px"
        
        

  
        self.endpoints = endpoints
        self.endpoints_dropdown_widget = endpoints_dropdown_widget
        self.refresh_method = refresh_method

        self.address_widget = self.ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width=widget_width
        )
        self.user_widget = self.ipywidget_factory.get_text(
            description='Username:',
            value='username',
            width=widget_width
        )
       
        self.password_widget = self.ipywidget_factory.get_text(
            description='Password:',
            value='password',
            width=widget_width
        )

        active_account = "None"
        try: 
            active_account=GoogleAuth.list_active_account()
        except BadUserConfigurationException: 
            active_account = "no account found"
        except GcloudNotInstalledException: 
            active_account = "no account found"
        
        accounts_list = {}
        try: 
            accounts_list.update(GoogleAuth.list_accounts_pairs())
        except BadUserConfigurationException: 
            accounts_list = {}
        except GcloudNotInstalledException: 
            accounts_list = {} 


        """
        self.google_credentials_widget = self.ipywidget_factory.get_text(
            description='Account:',
            value=active_account,
            width=widget_width,
            disabled=True
        )
        """
        self.google_credentials_widget = self.ipywidget_factory.get_dropdown(
            options= accounts_list,
            description=u"Credentialed Accounts:"
            
        )
        

        self.auth = self.ipywidget_factory.get_dropdown(
            options={constants.AUTH_KERBEROS: constants.AUTH_KERBEROS, constants.AUTH_GOOGLE: constants.AUTH_GOOGLE, constants.AUTH_BASIC: constants.AUTH_BASIC,
                     constants.NO_AUTH: constants.NO_AUTH},
            description=u"Auth type:"
        )

        # Submit widget
        self.submit_widget = self.ipywidget_factory.get_submit_button(
            description='Add endpoint'
        )

        self.auth.on_trait_change(self._show_correct_endpoint_fields)

        self.children = [self.ipywidget_factory.get_html(value="<br/>", width=widget_width),
                        self.address_widget, self.auth, self.user_widget, self.password_widget, self.google_credentials_widget,
                         self.ipywidget_factory.get_html(value="<br/>", width=widget_width), self.submit_widget]

        for child in self.children:
            child.parent_widget = self

        self._show_correct_endpoint_fields()

    def run(self):
        try: 
            endpoint = Endpoint(self.address_widget.value, self.auth.value, self.user_widget.value, self.password_widget.value)
            self.endpoints[self.address_widget.value] = endpoint
            self.ipython_display.writeln("Added endpoint {}".format(self.address_widget.value))
            # We need to call the refresh method because drop down in Tab 2 for endpoints wouldn't refresh with the new
            # value otherwise.
            self.refresh_method()
        except (BadUserDataException, BadUserConfigurationException) as error:
            ipython_display_new.writeln(u"endpoint url is wrong")
            raise error



    def _show_correct_endpoint_fields(self):
        if self.auth.value == constants.NO_AUTH or self.auth.value == constants.AUTH_KERBEROS:
            self.user_widget.layout.display = 'none'
            self.password_widget.layout.display = 'none'
            self.google_credentials_widget.layout.display = 'none'
        elif self.auth.value == constants.AUTH_GOOGLE:
            self.user_widget.layout.display = 'none'
            self.password_widget.layout.display = 'none'
            self.google_credentials_widget.layout.display = 'flex'
        else:
            self.user_widget.layout.display = 'flex'
            self.password_widget.layout.display = 'flex'
            self.google_credentials_widget.layout.display = 'none'
