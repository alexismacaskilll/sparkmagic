from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory

class Authenticator(object):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self, widget_width):
        self.login_service = u"None"
        self.url = 'http://example.com/livy'

    def get_widgets(self, widget_width): 
        ipywidget_factory = IpyWidgetFactory()
        
        self.address_widget = ipywidget_factory.get_text(
            description='Address:',
            value='http://example.com/livy',
            width=widget_width
        )
        widgets = [self.address_widget]
        return widgets 

    def update_with_widget_values(self): 
        self.url = self.address_widget.value
        
    def __call__(self, request):
        """subclasses should override"""
        return None
       
        
 