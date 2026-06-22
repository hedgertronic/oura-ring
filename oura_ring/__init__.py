"""Tools for acquiring and analyzing Oura API data.

Oura is a wearable ring for monitoring sleep, activity, and workouts. Learn more
about Oura at https://ouraring.com. Oura API v2 documentation can be found at
https://cloud.ouraring.com/v2/docs.
"""

from importlib.metadata import PackageNotFoundError, version

from oura_ring.auth import (
    AUTHORIZE_URL,
    REVOKE_URL,
    SCOPES,
    TOKEN_URL,
    OuraAuth,
)
from oura_ring.client import API_URL, OuraClient

try:
    __version__ = version("oura-ring")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "API_URL",
    "AUTHORIZE_URL",
    "REVOKE_URL",
    "SCOPES",
    "TOKEN_URL",
    "__version__",
    "OuraClient",
    "OuraAuth",
]
