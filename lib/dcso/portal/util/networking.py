# Copyright (c) 2020, DCSO GmbH

import socket
from urllib.parse import urlparse

from ..exceptions import PortalConfiguration

_API_URI_MAX_LEN = 300
_API_URI_SCHEMES = ('https', 'http')


def validate_api_url(url: str) -> str:
    """Validates URL as DCSO Portal API endpoint, and returns this
    validated URL.

    Raises `DCSOPortalConfiguration` when url argument is not valid.
    """
    url = url.strip()

    if not url:
        raise PortalConfiguration("API URL is required")

    if len(url) > 300:
        raise PortalConfiguration(f"API URL exceeds maximum of {_API_URI_MAX_LEN} characters")

    # URL should not have any query or fragment parts
    if '?' in url or '#' in url:
        raise PortalConfiguration(f"API URL must contain query or fragments")

    u = urlparse(url)

    if u.scheme not in _API_URI_SCHEMES:
        raise PortalConfiguration(f"API URL use unsupported scheme '{u.scheme}'")

    if not u.netloc:
        raise PortalConfiguration(f"API URL does not specify a domain")

    return url


def free_localhost_tcp_port() -> int:
    """Finds a free TCP port on the localhost (using address 127.0.0.1)."""
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port
