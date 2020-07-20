from .exceptions import BadUserDataException, BadUserConfigurationException
from sparkmagic.utils.constants import AUTHS_SUPPORTED
from sparkmagic.livyclientlib.endpoint import Endpoint

class GoogleEndpoint(Endpoint):
    def __init__(self, url, auth, username="", password="", implicitly_added=False, project_id="", region= "", credentialed_account= "None" ):
        super(GoogleEndpoint, self).__init__(url, auth, username, password, implicitly_added)
        """
        if not url:
            raise BadUserDataException(u"URL must not be empty")
        if auth not in AUTHS_SUPPORTED:
            raise BadUserConfigurationException(u"Auth '{}' not supported".format(auth))
        """
        self.region = region
        self.project_id = project_id
        self.credentialed_account = credentialed_account
    

    def __eq__(self, other):
        if type(other) is not GoogleEndpoint:
            return False     
        return self.url == other.url and self.username == other.username and self.password == other.password and self.auth == other.auth 

    def __hash__(self):
        return hash((self.url, self.username, self.password, self.auth))

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return u"GoogleEndpoint({})".format(self.url)
