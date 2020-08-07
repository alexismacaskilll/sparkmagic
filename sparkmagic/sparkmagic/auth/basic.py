"""Class for implementing a basic access authenticator for SparkMagic"""

from hdijupyterutils.ipywidgetfactory import IpyWidgetFactory
from requests.auth import HTTPBasicAuth
from .customauth import Authenticator


class Basic(HTTPBasicAuth, Authenticator):
    """Basic access authenticator for SparkMagic"""
    def __init__(self):
        self.username = 'username'
        self.password = 'password'
        HTTPBasicAuth.__init__(self, self.username, self.password)
        Authenticator.__init__(self)

    def get_widgets(self, widget_width):
        """Creates and returns a list with an address, username, and password widget

        Args:
            widget_width (str): The width of all widgets to be created.

        Returns:
            Sequence[hdijupyterutils.ipywidgetfactory.IpyWidgetFactory]: list of widgets
        """
        ipywidget_factory = IpyWidgetFactory()

        self.user_widget = ipywidget_factory.get_text(
            description='Username:',
            value=self.username,
            width=widget_width
        )

        self.password_widget = ipywidget_factory.get_text(
            description='Password:',
            value=self.password,
            width=widget_width
        )

        widgets = [self.user_widget, self.password_widget]
        return Authenticator.get_widgets(self, widget_width) + widgets

    def update_with_widget_values(self):
        """Updates url, username, and password to be the value of their respective widgets."""
        Authenticator.update_with_widget_values(self)
        self.username = self.user_widget.value
        self.password = self.password_widget.value

    def __call__(self, request):
        return HTTPBasicAuth.__call__(self, request)

    def __hash__(self):
        return id(self)
