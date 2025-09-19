import time

import jwt

from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from jsm_user_services.drf.exceptions import ExpiredToken
from jsm_user_services.drf.exceptions import InvalidToken
from jsm_user_services.drf.exceptions import NotAuthenticated
from jsm_user_services.services.user import current_jwt_token
from jsm_user_services.support.auth_jwt import decode_jwt_token


class OauthJWTAuthentication(BaseAuthentication):
    """
    Authentication class for OAuth JWT tokens.
    Should be used in DRF views that need to use Auth0 tokens.
    """

    def authenticate(self, request: Request) -> tuple[AnonymousUser, str] | None:
        token = current_jwt_token()
        if token is None:
            raise NotAuthenticated()

        try:
            payload = decode_jwt_token(token)
            current_timestamp = int(time.time())
            is_token_expired = "exp" in payload and current_timestamp > payload["exp"]
            is_sub_claim_in_payload = "sub" in payload
            if not is_token_expired and is_sub_claim_in_payload:
                return (AnonymousUser(), token)
            else:
                raise InvalidToken()
        except jwt.DecodeError:
            raise InvalidToken()


class LvJWTAuthentication(BaseAuthentication):
    """
    Authentication class for LV JWT tokens.
    Should be used in DRF views that need to use LV tokens.
    """

    def authenticate(self, request: Request) -> tuple[AnonymousUser, str] | None:
        token = current_jwt_token()
        if token is None:
            raise NotAuthenticated()

        try:
            payload = decode_jwt_token(token)
        except jwt.DecodeError as e:
            raise InvalidToken() from e
        except jwt.ExpiredSignatureError as e:
            raise ExpiredToken() from e

        # Set the payload in the request
        setattr(request, "jwt_payload", payload)

        return (AnonymousUser(), token)
