import clearskies.di

from .jwks import Jwks


class AuthorizationPassThrough(Jwks):
    """
    Authentication class with pass through.

    This authentication class takes the authentication header from the incoming request and reflects
    it on outgoing requests.
    """

    """
    The input output helper
    """
    input_output = clearskies.di.inject.InputOutput()

    def headers(self, retry_auth=False):
        return {"Authorization": self.input_output.request_headers.get("authorization", True)}
