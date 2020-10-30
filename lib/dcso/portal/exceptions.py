# Copyright (c) 2020, DCSO GmbH

"""
Definition of exceptions raised by the `dcso.portal` module.
"""

from dcso.glosom.glosom import GlosomException


class PortalException(Exception):
    """Base exception for Portal related exceptions."""
    pass


class PortalConnection(PortalException):
    """Exception raised on any kind of connection issue."""
    pass


class PortalConfiguration(PortalException):
    """Exception raised on configuration issues."""
    pass


class PortalAPIRequest(PortalConnection):
    """Exception raised on API request issues."""
    pass


class PortalAPIError(GlosomException, PortalException):
    """Exception raised with the error received from the API."""


class PortalAPIResponse(PortalException):
    """Exception raised when API response is not valid or could not be used."""
