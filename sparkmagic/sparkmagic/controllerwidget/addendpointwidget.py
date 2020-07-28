# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
from .abstractmenuwidget import AbstractMenuWidget
from sparkmagic.livyclientlib.endpoint import Endpoint
import sparkmagic.utils.constants as constants
import sparkmagic.utils.configuration as conf
import importlib
import logging 
import sys
from collections import defaultdict
import json

class AddEndpointWidget(AbstractMenuWidget):

    def __init__(self, spark_controller, ipywidget_factory, ipython_display, endpoints, endpoints_dropdown_widget,
                 refresh_method):
        # This is nested
        super(AddEndpointWidget, self).__init__(spark_controller, ipywidget_factory, ipython_display, True)
      
        widget_width = "800px"

        self.endpoints = endpoints
        self.endpoints_dropdown_widget = endpoints_dropdown_widget
        self.refresh_method = refresh_method
        #map auth class path string to the instance of the class. 
        self.auth_instances = {}
        for auth in conf.auths_supported().values(): 
            module, class_name = (auth).rsplit('.', 1)
            events_handler_module = importlib.import_module(module)
            auth_class = getattr(events_handler_module, class_name)
            self.auth_instances[auth] = auth_class()


        #options={constants.AUTH_KERBEROS: constants.AUTH_KERBEROS, constants.AUTH_BASIC: constants.AUTH_BASIC, constants.NO_AUTH: constants.NO_AUTH}
        self.auth_type = self.ipywidget_factory.get_dropdown(
            options = conf.auths_supported(),
            description=u"Auth type:"
        )

        #defaultdict maps keys to list of values. .values() should then just return all of the values in one list not nested arrays. 
        # maps instance to list of instances widgets. Useful so we can turn off / on display for widgets on dropdown change 
        self.authWidgets = defaultdict(list)
        for _class, instance in self.auth_instances.items():
            widgets =  instance.get_widgets()
            for widget in widgets: 
                if  (_class == self.auth_type.value): 
                    widget.layout.display = 'flex'
                    self.auth = instance
                else: 
                    widget.layout.display = 'none'
                self.authWidgets[instance].append(widget)
            
       
        """
        self.address_widget = self.ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width=widget_width
        )
        """
        
        # Submit widget
        self.submit_widget = self.ipywidget_factory.get_submit_button(
            description='Add endpoint'
        )
 
        self.auth_type.on_trait_change(self._update_auth)
        
        dropdown_auth = [self.ipywidget_factory.get_html(value="<br/>", width=widget_width)]
        drop = [self.auth_type]
        custom = self.authWidgets.values()
        submitT  = [self.ipywidget_factory.get_html(value="<br/>", width=widget_width)]
        submit = [self.submit_widget]

        self.children = dropdown_auth + drop + custom + submitT + submit

        for child in self.children:
            child.parent_widget = self
        
        self._update_auth()
        



    def run(self):
        endpoint = Endpoint(self.auth.url, self.auth)

        self.endpoints[self.auth.url] = endpoint
        self.ipython_display.writeln("Added endpoint {}".format(self.auth.url))
        # We need to call the refresh method because drop down in Tab 2 for endpoints wouldn't refresh with the new
        # value otherwise.
        self.refresh_method()

    

    def _update_auth(self): 
        """
        Create an instance of the chosen auth type maps to in the config file.
        """
        #go through all widgets of old self.auth instance, and turn it off
        for widget in self.authWidgets[self.auth]: 
            widget.layout.display = 'none'

        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logger = logging.getLogger('LOGGER_NAME')
        #set self.auth to the auth instance the dropdown class maps to 
        self.auth = self.auth_instances.get(self.auth_type.value)
        #go through all widgets of new self.auth instance, and turn their display on 
        for widget in self.authWidgets[self.auth]: 
            widget.layout.display = 'flex'

       
        """


        n = 3
        # Replace the element at index 3 to 
        self.children = self.children [ : n] + (self.auth.get_widgets() ,) + self.children [n + 1 : ]
        
        self.auth.address_widget.layout.display = 'flex'
        """
        
