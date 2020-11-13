# Copyright (c) 2020, DCSO GmbH

import struct
from typing import NoReturn, Optional, Tuple, Union

from .constants import *


class Glosom:
    """
    Glosom - Global Service Oriented Messages

    A GLOSOM is a message with a code which has the type of message, the group, the message ID,
    and the service that generate the message. The code itself is a 32-bit integer.

    The message of a GLOSOM is used for showing humans. The code however, is meant for scripts,
    applications, and robots.
    """

    def __init__(self, message: str = '',
                 code: Optional[Union[int, str]] = 0,
                 message_id: int = 0, group: int = 0, gtype: int = TYPE_ERROR, service: int = 0x00):
        """

        :param message: human readable string of the message
        :param code: GLOSOM code which can be decoded in message type, group, message ID, and service
        :param message_id: message ID of the glosom (1 .. 2^16)
        :param group: group of the message (see constants GROUP_*)
        :param gtype: type of the message (info, error, ..)
        :param service: service that produced the message (globally defined outside this package, max 2^8-2)
        """
        self._code: int = 0
        self.message: str = message
        self.message_id: int = message_id
        self.service: int = service
        self.group: int = group
        self.type: int = gtype

        if not code:
            self._code = self.encode()
        else:
            self.code = code

    @property
    def code(self) -> int:
        return self._code

    @code.setter
    def code(self, value: Optional[Union[int, str]] = 0) -> NoReturn:
        """Set value as code for this GLOSOM

        The value argument can be either an int or a str. If str, conversion
        to int is tried, then hexadecimal with '0x' prefix, and finally
        hexadecimal without '0x'. If the conversion fails, code is considered 0 (zero).

        :param value: GLOSOM code as int or hexadecimal string
        """
        if value and isinstance(value, str):
            try:
                self._code = int(value)
            except ValueError as exc:
                # keep trying
                try:
                    self._code = int(value, 0)
                except ValueError:
                    # and keep trying more
                    try:
                        self._code = int(value, 16)
                    except ValueError:
                        # give up; silently set code to 0
                        self._code = 0
        elif value:
            self._code = value

        b = struct.pack('>I', self._code)
        self.message_id = (b[1] << 8) | b[2]
        self.service = b[3]
        self.group = b[0] & ~0xF0
        self.type = b[0] >> 4

    def encode(self) -> int:
        """Encodes the GLOSOM information into a GLOSOM code

        The int returned is an unsigned 32 integer. It is advised, when presenting it,
        to use the canonical hexadecimal notation.

        :return: GLOSOM code as int
        """
        b = bytearray(4)
        b[0], b[3] = self.type | self.group, self.service
        b[1], b[2] = struct.pack('>H', self.message_id)
        return struct.unpack('>I', b)[0]

    def graphql_error(self) -> dict:
        """Convenience method return dict suitable for returning GraphQL error

        The returned dictionary is suitable to encode as JSON for GraphQL returning
        the GLOSOM as error. The extensions contains the code as integer.

        :return: GraphQL error as dict
        """
        return {
            'errors': [
                {
                    'message': self.message,
                    'extensions': {
                        'code': self.encode()
                    }
                }
            ]
        }


class GlosomException(Exception):
    """Exception storing a GLOSOM
    """

    def __init__(self, glosom: Glosom):
        self.glosom = glosom

    def __str__(self) -> str:
        if self.glosom.message_id == 0:
            # try with non-GLOSOM
            if self.glosom.message != "":
                return self.glosom.message
            return "invalid message"
        else:
            return "{msg} ({code:X})".format(msg=self.glosom.message, code=self.glosom.code)
