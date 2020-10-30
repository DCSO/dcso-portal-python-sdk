# Copyright (c) 2020, DCSO GmbH

from datetime import datetime
from typing import Optional

from .rbac import RBACMixin
from .token import Token
from ..abstracts import APIAbstract
from ..exceptions import PortalAPIResponse, PortalException
from ..util.graphql import GraphQLRequest

_DEFAULT_TOKEN_RESOURCE = "PortalPythonSDK"


class Authentication:
    def __init__(self, graphql_response: Optional[dict]):
        self.id: str = ''
        self.username: str = ''
        self.token: Optional[Token] = None
        self.token_is_temporary: bool = False
        self.groups = []  # legacy: replaced by permissions

        self.totp_required: bool = True
        self.totp_activated: Optional[datetime] = None
        self.totp_qrcode: Optional[str] = None

        if graphql_response:
            self._handle_graphql_response(graphql_response)

    def _handle_graphql_response(self, res: dict):
        try:
            self.token = Token(graphql_response=res)

            if res['user']:
                self.id = res['user']['id']
                self.username = res['user']['username']

            self.totp_required = res['otp']['required']
            self.totp_activated = res['otp']['activated']
            self.token_is_temporary = res['isTemporaryToken']
        except KeyError as exc:
            raise PortalAPIResponse(f"failed handling authentication response ({exc})")


class Auth(RBACMixin):
    """Auth provides authentication, authorization, and user management.

    Typical use:

        api = APIClient('https://api.example.com/api')
        auth = Auth(api)
        user = auth.authenticate("alice", "alice.password")
    """

    @property
    def token(self) -> str:
        return self._api.token

    @token.setter
    def token(self, token: str) -> None:
        self._api.token = token

    def __init__(self, api: APIAbstract):
        self._api: APIAbstract = api

    def authenticate(self, username: str, password: str, resource: str = _DEFAULT_TOKEN_RESOURCE,
                     set_api_token: bool = True) -> Authentication:
        """Authenticates with DCSO Portal using credentials or `username` and `password`,
        for the given `resource`. Resource is by default `PortalPythonSDK`, but it can
        be, for example, the name of the application or script.

        When the authenticating user has two-factor authentication (2FA) enforced, a second
        pass is needed using the temporary token received with by method and passed
        on to the `second_authentication_totp` method.

        When `set_api_token` is True, and authentication succeeds, the non-temporary
        token will be stored and used for further API queries.

        An Authentication instance is returned which contains general user information,
        token, and details about this token.

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        variables = {
            "portalauth": {
                "username": username,
                "password": password,
                "resource": resource
            }
        }

        request = GraphQLRequest(api_url=self._api.api_url,
                                 query=_GRAPHQL_MUTATION_AUTHN, variables=variables)

        try:
            response = request.execute_dict()
        except PortalException:
            raise

        try:
            authn = Authentication(graphql_response=response['data']['portalauth'])
            if not authn.token_is_temporary and set_api_token:
                self._api.token = authn.token.token
            return authn
        except PortalAPIResponse:
            raise

    def second_authentication_totp(self, username: str, temp_token: str, totp: str,
                                   set_api_token: bool = True) -> Authentication:
        """Two-factor authentication using Time-based One-Time Password (TOTP).

        The `username` must be the same which was used with the `authenticate` method. The
        `temp_token` argument is set to the temporary token returned by the method
        `authenticate`. Finally, the `totp` argument is the code visible in the
        authenticator application which holds the TOTP secret.

        When `set_api_token` is True, and authentication succeeds, the non-temporary
        token will be stored and used for further API queries.

        An Authentication instance is returned which contains general user information,
        token, and details about this token.

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        variables = {
            "portalauth": {
                "username": username,
                "temporaryToken": temp_token,
                "otpCode": totp,
            }
        }

        request = GraphQLRequest(api_url=self._api.api_url,
                                 query=_GRAPHQL_MUTATION_AUTHN, variables=variables)

        try:
            response = request.execute_dict()
        except PortalException:
            raise

        try:
            authn = Authentication(graphql_response=response['data']['portalauth'])
            if set_api_token:
                self._api.token = authn.token.token
            return authn
        except PortalAPIResponse:
            raise

    def refresh_jwt_token(self, username: str, token: str, resource: str = _DEFAULT_TOKEN_RESOURCE,
                          set_api_token: bool = True) -> Authentication:
        """Refreshes a User Token (JWT) with DCSO Portal

        JWTs (JSON Web Tokens) usually have a short lifespan, but they can be refreshed
        provided the previous `token` is still valid. The `username` and `resource` must
        match those of the original token.  A new token will be returned, rendering
        previous unusable.

        An Authentication instance is returned which contains general user information,
        token, and details about this token.

        Raises `PortalAPIError` When the GraphQL API endpoint returned an error.
        When there was an issue with the request itself, or decoding JSON failed,
        the `PortalAPIRequest` exception is raised.
        """
        variables = {
            "portalauth": {
                "username": username,
                "refreshToken": token,
                "resource": resource,
            }
        }

        request = GraphQLRequest(api_url=self._api.api_url,
                                 query=_GRAPHQL_MUTATION_AUTHN, variables=variables)

        try:
            response = request.execute_dict()
        except PortalException as exc:
            raise

        try:
            authn = Authentication(graphql_response=response['data']['portalauth'])
            if set_api_token:
                self._api.token = authn.token.token
            return authn
        except PortalAPIResponse:
            raise


_GRAPHQL_MUTATION_AUTHN = """
mutation ($portalauth: auth_AuthorizationInput!) {
  portalauth: auth_createAuthorization(input: $portalauth) {
    user {
        id
        username
        accessTo {
            service { id code }
            group { code }
        }
    }
    token
    isTemporaryToken
    otp {
      required
      activated
    }
    otpSVGQRCode
  }
}
"""
