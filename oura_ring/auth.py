"""OAuth2 support for the Oura API v2.

Oura deprecated personal access tokens in December 2025; OAuth2 is now the only
way to obtain credentials for a new integration. This module implements the
Authorization Code grant (server-side flow), which is the only flow Oura's
OpenAPI spec declares and the only one that issues refresh tokens.

Oura API authentication docs: https://cloud.ouraring.com/docs/authentication

Flow overview:
    1. Send the user to ``authorize_url(...)`` to grant access.
    2. Oura redirects back to your ``redirect_uri`` with a ``code`` query param.
    3. Exchange that code for tokens with ``exchange_code(code)``.
    4. When the access token expires, call ``refresh_token(refresh_token)``.

Example:
    from oura_ring import OuraClient, OuraAuth

    oauth = OuraAuth(client_id, client_secret)

    # 1-2. Redirect the user, capture the `code` from the callback.
    url = oauth.authorize_url(redirect_uri="https://example.com/callback")

    # 3. Exchange the code. Persist the whole token dict.
    tokens = oauth.exchange_code(code, redirect_uri="https://example.com/callback")

    client = OuraClient(access_token=tokens["access_token"])

    # 4. Later, refresh. Refresh tokens are single-use: persist the NEW
    #    refresh_token returned here, or the next refresh will fail.
    tokens = oauth.refresh_token(tokens["refresh_token"])
"""

from __future__ import annotations

from typing import Any, cast
from urllib.parse import urlencode

import requests

AUTHORIZE_URL = "https://cloud.ouraring.com/oauth/authorize"
TOKEN_URL = "https://api.ouraring.com/oauth/token"
REVOKE_URL = "https://api.ouraring.com/oauth/revoke"

# OAuth2 scopes Oura recognizes. The first eight are the only ones declared in
# Oura's published OpenAPI spec (the SpO2 scope is `spo2Daily` there, though the
# human-readable auth guide calls it `spo2`). The last three are enforced by the
# live API but absent from the spec — observed as 401s on daily_resilience
# (`stress`), vO2_max / daily_cardiovascular_age (`heart_health`), and
# ring_battery_level (`ring_configuration`) — so this list may still be
# non-exhaustive. `authorize_url()` requests all scopes the app is approved for
# when no explicit list is passed, which avoids depending on this list being complete.
SCOPES = (
    "email",
    "personal",
    "daily",
    "heartrate",
    "workout",
    "tag",
    "session",
    "spo2Daily",
    "stress",
    "heart_health",
    "ring_configuration",
)


class OuraAuth:
    """Acquire and refresh Oura API access tokens via the Authorization Code grant.

    Args:
        client_id (str): OAuth2 client id from the Oura developer portal.
        client_secret (str): OAuth2 client secret from the Oura developer portal.
    """

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def authorize_url(
        self,
        redirect_uri: str | None = None,
        scope: list[str] | tuple[str, ...] | None = None,
        state: str | None = None,
    ) -> str:
        """Build the URL to send the user to for granting access.

        Args:
            redirect_uri (str, optional): Where Oura redirects after authorization.
                Must exactly match a URI whitelisted on the app. May be omitted only
                if the app has exactly one configured redirect URI.
            scope (list[str], optional): Scopes to request. Defaults to None, which
                omits the ``scope`` param so Oura grants every scope the application
                is approved for. Pass an explicit list (see ``SCOPES``) to request a
                narrower set.
            state (str, optional): Opaque value echoed back on redirect. Strongly
                recommended for CSRF protection.

        Returns:
            str: The authorization URL to redirect the user to.
        """
        params: dict[str, str] = {
            "response_type": "code",
            "client_id": self.client_id,
        }

        # Omitting `scope` asks Oura for all scopes the app is approved for. Since
        # the published spec under-documents scopes, this is more robust than
        # forcing a list that may be incomplete.
        if scope is not None:
            params["scope"] = " ".join(scope)

        if redirect_uri:
            params["redirect_uri"] = redirect_uri

        if state:
            params["state"] = state

        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(
        self, code: str, redirect_uri: str | None = None
    ) -> dict[str, Any]:
        """Exchange an authorization code for an access/refresh token pair.

        Args:
            code (str): The ``code`` query param Oura returned to your redirect URI.
            redirect_uri (str, optional): Must match the ``redirect_uri`` used in
                ``authorize_url``.

        Returns:
            dict[str, Any]: Token response. Keys: ``token_type`` ("bearer"),
                ``access_token``, ``expires_in`` (seconds), ``refresh_token``.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        if redirect_uri:
            data["redirect_uri"] = redirect_uri

        return self._token_request(data)

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Exchange a refresh token for a fresh access/refresh token pair.

        Refresh tokens are single-use: the one passed here is invalidated and the
        response contains a NEW ``refresh_token``. Persist it or the next refresh
        will fail.

        Args:
            refresh_token (str): The current refresh token.

        Returns:
            dict[str, Any]: Token response. Keys: ``token_type``, ``access_token``,
                ``expires_in``, ``refresh_token``.
        """
        return self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )

    def revoke_token(self, access_token: str) -> None:
        """Revoke an Oura API access token.

        Args:
            access_token (str): The access token to revoke.
        """
        response = requests.get(
            REVOKE_URL,
            params={"access_token": access_token},
            timeout=60,
        )
        response.raise_for_status()

    def _token_request(self, data: dict[str, str]) -> dict[str, Any]:
        response = requests.post(TOKEN_URL, data=data, timeout=60)
        response.raise_for_status()
        return cast("dict[str, Any]", response.json())
