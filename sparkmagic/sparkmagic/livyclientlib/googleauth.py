from requests.auth import AuthBase
import requests



class HTTPGoogleAuth(AuthBase):
    """Attaches HTTP Google Auth Authentication to the given Request
    object."""

    def __init__(self, token = None):
        self.token = token
    
    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return request

    
    