# Copyright (c) 2015  aggftw@gmail.com
# Distributed under the terms of the Modified BSD License.
from .abstractmenuwidget import AbstractMenuWidget
from sparkmagic.livyclientlib.endpoint import Endpoint
import sparkmagic.utils.constants as constants
import sparkmagic.utils.configuration as conf
import importlib
import logging 

class AddEndpointWidget(AbstractMenuWidget):

    def __init__(self, spark_controller, ipywidget_factory, ipython_display, endpoints, endpoints_dropdown_widget,
                 refresh_method):
        # This is nested
        super(AddEndpointWidget, self).__init__(spark_controller, ipywidget_factory, ipython_display, True)
      
        widget_width = "800px"

        self.endpoints = endpoints
        self.endpoints_dropdown_widget = endpoints_dropdown_widget
        self.refresh_method = refresh_method


        #options={constants.AUTH_KERBEROS: constants.AUTH_KERBEROS, constants.AUTH_BASIC: constants.AUTH_BASIC, constants.NO_AUTH: constants.NO_AUTH}
        self.auth_type = self.ipywidget_factory.get_dropdown(
            options = conf.auths_supported(),
            description=u"Auth type:"
        )


        module, class_name = (self.auth_type.value).rsplit('.', 1)
        
        events_handler_module = importlib.import_module(module)
        auth_class = getattr(events_handler_module, class_name)
        self.auth = auth_class()
       
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
        """
        self.children = []
        self.children.append(self.ipywidget_factory.get_html(value="<br/>", width=widget_width))
        self.children.append(self.auth_type)
        self.children.append(self.auth.get_widgets())
        self.children.append(self.ipywidget_factory.get_html(value="<br/>", width=widget_width))
        self.children.append(self.submit_widget)
        """
         #also will have to add to children?
        self.children = [self.ipywidget_factory.get_html(value="<br/>", width=widget_width),
                        self.auth_type, self.auth.get_widgets(),
                        self.ipywidget_factory.get_html(value="<br/>", width=widget_width), self.submit_widget]


        #self.children = [self.ipywidget_factory.get_html(value="<br/>", width=widget_width), self.auth_type]
        #here we add the url widget from authenticator. I have this because google auth changes value of url widget depending 
        #on what cluster project and region they enter, but will probably move url widget to this class and just set its 
        #value in the google auth. This is primarily to see if this will work for other things like adding in the project 
        #id textbox for google. 
    
        #self.children = self.children.append([self.ipywidget_factory.get_html(value="<br/>", width=widget_width), self.submit_widget])
        
        for child in self.children:
            child.parent_widget = self
        
        self._update_auth()
        


    def run(self):
        endpoint = Endpoint(self.auth.url(), self.auth)

        self.endpoints[self.auth.url()] = endpoint
        #getting this url could also be an issue 
        self.ipython_display.writeln("Added endpoint {}".format(self.auth.url()))
        # We need to call the refresh method because drop down in Tab 2 for endpoints wouldn't refresh with the new
        # value otherwise.
        self.refresh_method()

    

    def _update_auth(self): 
        """
        Create an instance of the chosen auth type maps to in the config file.
        """
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logger = logging.getLogger('LOGGER_NAME')
        module, class_name = (self.auth_type.value).rsplit('.', 1)
        logger.info(dir(module))
        logger.info(module)
        logger.info(class_name)
        
        events_handler_module = importlib.import_module(module)
        logger.info(events_handler_module)

        logger.info(dir(events_handler_module))
        auth_class = getattr(events_handler_module, class_name)
        self.auth = auth_class()
        

