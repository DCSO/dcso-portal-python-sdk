# Copyright (c) 2020, DCSO GmbH

import base64
import binascii
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..exceptions import PortalAPIResponse
from ..util.temporal import diff_utc_now, utc_now


def pad_base64(b: str) -> str:
    return b + ('=' * (len(b) % 4))


class Token:
    def __init__(self, graphql_response: Optional[dict]):
        self.token: str = ''
        self._is_temporary: bool = False
        self.expires: Optional[datetime] = None

        if graphql_response:
            self._handle_graphql_response(graphql_response)

    @property
    def is_temporary(self) -> bool:
        return self._is_temporary

    def _handle_graphql_response(self, res: dict):
        try:
            self.token = res['token']
            self._is_temporary = res['isTemporaryToken']
        except KeyError as exc:
            raise PortalAPIResponse(f"failed handling token information ({exc})")

        if '.' in self.token:
            self._handle_jwt(self.token)

    def _handle_jwt(self, token: str):
        bad_jwt = "malformed user token ({reason})"
        try:
            base64_header, base64_payload, base64_signature = token.split('.')
        except ValueError:
            raise PortalAPIResponse(bad_jwt.format(reason="parts check"))

        try:
            header = json.loads(base64.b64decode(pad_base64(base64_header)).decode())
            payload = json.loads(base64.b64decode(pad_base64(base64_payload)).decode())
        except (binascii.Error, UnicodeError) as exc:
            raise PortalAPIResponse(bad_jwt.format(reason="decode JSON; " + str(exc)))

        if header['typ'] != 'JWT':
            raise PortalAPIResponse(bad_jwt.format(reason="not JWT"))

        try:
            self.expires = datetime.utcfromtimestamp(payload['exp']).replace(tzinfo=timezone.utc)
        except (OverflowError, OSError, KeyError):
            raise PortalAPIResponse(bad_jwt.format(reason="bad expire"))

        if self.is_expired():
            raise PortalAPIResponse(bad_jwt.format(reason="expired"))

        self._is_temporary = not payload['authz']['groups']

    def is_expired(self) -> bool:
        return self.expires <= utc_now()

    def expires_in(self) -> timedelta:
        if self.expires:
            return diff_utc_now(self.expires)

        return timedelta(0)
