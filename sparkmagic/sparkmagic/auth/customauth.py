from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
from sparkmagic.utils.constants import WIDGET_WIDTH

class Authenticator(object):
    """Base class for implementing an authentication provider for SparkMagic"""
    def __init__(self):
        self.url = 'http://example.com/livy'
        self.widgets = self.get_widgets(WIDGET_WIDTH)

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

    def __hash__(self):
        return id(self)
       