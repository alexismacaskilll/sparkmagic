# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
from sparkmagic.controllerwidget.abstractmenuwidget import AbstractMenuWidget
from sparkmagic.livyclientlib.endpoint import Endpoint
from sparkmagic.livyclientlib.google_endpoint import GoogleEndpoint
#maybe import 
import sparkmagic.utils.constants as constants
import sparkmagic.livyclientlib.googleauth as GoogleAuth
from sparkmagic.livyclientlib.exceptions import GcloudNotInstalledException, BadUserConfigurationException
from google.auth.exceptions import UserAccessTokenError


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

        # we need to make this widget pluggable just incase there is a custom thing.  
        #all of this should be in custom widget
        active_account = "None"
        try: 
            active_account=GoogleAuth.list_active_account()
        except BadUserConfigurationException: 
            active_account = "None"
        except GcloudNotInstalledException: 
            active_account = "None"
        
        accounts_list = {}
        try: 
            accounts_list.update(GoogleAuth.list_accounts_pairs())
        except BadUserConfigurationException: 
            accounts_list = {}
        except GcloudNotInstalledException: 
            accounts_list = {} 

        self.cluster_name_widget = self.ipywidget_factory.get_text(
            description='Cluster:',
            value='amacaskill-livy',
            width=widget_width
        )

        self.project_widget = self.ipywidget_factory.get_text(
            description='Project:',
            value='google.com:hadoop-cloud-dev',
            width=widget_width
        )
        self.region_widget = self.ipywidget_factory.get_text(
            description='Region:',
            value='us-central1',
            width=widget_width
        )

        
        self.google_credentials_widget = self.ipywidget_factory.get_dropdown(
            options= accounts_list,
            description=u"Account:"
        )

        if active_account != "None": 
            self.google_credentials_widget.value = active_account



        #change to having custom auth and we will have the value be an instance of the GoogleAuth Authenticator instead of string. 
        #but we will have to explicitly add thiis. 
        # 
        self.auth = self.ipywidget_factory.get_dropdown(
            options={constants.AUTH_KERBEROS: constants.AUTH_KERBEROS, constants.AUTH_GOOGLE: constants.AUTH_GOOGLE, constants.AUTH_BASIC: constants.AUTH_BASIC,
                     constants.NO_AUTH: constants.NO_AUTH},
            description=u"Auth type:"
        )

        # Submit widget
        self.submit_widget = self.ipywidget_factory.get_submit_button(
            description='Add endpoint'
        )

        #here we need to check if isinstance(self.auth, Authenticator) -> then we want to do self.auth._show_correct_endpoint_fields 
        # so this is another method we want to have in Authenticator class 
        self.auth.on_trait_change(self._show_correct_endpoint_fields)
     
        #also will have to add to children?
        self.children = [self.ipywidget_factory.get_html(value="<br/>", width=widget_width),
                        self.address_widget, self.auth, self.user_widget, self.password_widget, self.google_credentials_widget,self.project_widget, self.cluster_name_widget, self.region_widget,
                        self.ipywidget_factory.get_html(value="<br/>", width=widget_width), self.submit_widget]

        for child in self.children:
            child.parent_widget = self
        self._show_correct_endpoint_fields()


    def run(self):
        #if isinstance(self.auth.value, Authenticator) -> then we need to get all the fields. Because run has to stay in this
        if self.auth.value == constants.AUTH_GOOGLE: 
            component_gateway_url = GoogleAuth.get_component_gateway_url(self.cluster_name_widget.value, self.project_widget.value, self.region_widget.value)
            #endpoint = the custom endpoint type. We will pass in values like custom widget.auth.value
            endpoint = GoogleEndpoint(component_gateway_url, self.auth.value, self.user_widget.value, self.password_widget.value, False, self.cluster_name_widget.value, self.project_widget.value, self.region_widget.value, self.google_credentials_widget.value)
            self.endpoints[component_gateway_url] = endpoint
            self.ipython_display.writeln("Added endpoint {}".format(component_gateway_url))
            self.refresh_method()
        else: 
            endpoint = Endpoint(self.address_widget.value, self.auth.value, self.user_widget.value, self.password_widget.value)
            self.endpoints[self.address_widget.value] = endpoint
            self.ipython_display.writeln("Added endpoint {}".format(self.address_widget.value))
            self.refresh_method()

        # We need to call the refresh method because drop down in Tab 2 for endpoints wouldn't refresh with the new
        # value otherwise.
        #self.refresh_method()


    #will also need this is custom widget
    def _show_correct_endpoint_fields(self):
        if self.auth.value == constants.NO_AUTH or self.auth.value == constants.AUTH_KERBEROS:
            self.user_widget.layout.display = 'none'
            self.password_widget.layout.display = 'none'
            self.google_credentials_widget.layout.display = 'none'
            self.cluster_name_widget.layout.display = 'none'
            self.project_widget.layout.display = 'none'
            self.region_widget.layout.display = 'none'
        
        #if isinstance(self.auth.value, Authenticator) -> then we need to display right widgets. These widgets
        # should be created in a different class that extends this one.
        elif self.auth.value == constants.AUTH_GOOGLE:
            self.user_widget.layout.display = 'none'
            self.password_widget.layout.display = 'none'
            self.google_credentials_widget.layout.display = 'flex'
            self.cluster_name_widget.layout.display = 'flex'
            self.address_widget.layout.display = 'none'
            self.project_widget.layout.display = 'flex'
            self.region_widget.layout.display = 'flex'
            
        else:
            self.user_widget.layout.display = 'flex'
            self.password_widget.layout.display = 'flex'
            self.google_credentials_widget.layout.display = 'none'
            self.cluster_name_widget.layout.display = 'none'
            self.project_widget.layout.display = 'none'
            self.region_widget.layout.display = 'none'

