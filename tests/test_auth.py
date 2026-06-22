"""Tests for oura_ring.auth.OuraAuth.

requests.post is mocked; no live network calls and no real credentials are used.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest

from oura_ring import REVOKE_URL, SCOPES, TOKEN_URL, OuraAuth

CLIENT_ID = "fake_client_id"
CLIENT_SECRET = "fake_client_secret"


def _client():
    return OuraAuth(CLIENT_ID, CLIENT_SECRET)


def _query(url):
    return parse_qs(urlparse(url).query)


# ----------------------------------------------------------------------------------
# authorize_url


def test_authorize_url_default_omits_scope():
    # With no explicit scope, the param is omitted so Oura grants every scope the
    # app is approved for (the published spec under-documents scopes).
    url = _client().authorize_url()
    assert url.startswith("https://cloud.ouraring.com/oauth/authorize?")

    q = _query(url)
    assert q["response_type"] == ["code"]
    assert q["client_id"] == [CLIENT_ID]
    assert "scope" not in q
    assert "redirect_uri" not in q
    assert "state" not in q


def test_authorize_url_explicit_all_scopes():
    url = _client().authorize_url(scope=SCOPES)
    q = _query(url)
    assert q["scope"] == [" ".join(SCOPES)]


def test_authorize_url_custom_scope_redirect_and_state():
    url = _client().authorize_url(
        redirect_uri="https://example.com/callback",
        scope=["daily", "heartrate"],
        state="xyz",
    )
    assert url.startswith("https://cloud.ouraring.com/oauth/authorize?")

    q = _query(url)
    assert q["scope"] == ["daily heartrate"]
    assert q["redirect_uri"] == ["https://example.com/callback"]
    assert q["state"] == ["xyz"]
    assert q["client_id"] == [CLIENT_ID]
    assert q["response_type"] == ["code"]


# ----------------------------------------------------------------------------------
# exchange_code


def test_exchange_code_posts_authorization_code_grant():
    token_body = {"access_token": "fake_access", "refresh_token": "fake_refresh"}
    with patch("requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            **{"json.return_value": token_body, "raise_for_status.return_value": None}
        )
        result = _client().exchange_code(
            "fake_code", redirect_uri="https://example.com/callback"
        )

    assert result == token_body
    assert mock_post.call_args.args[0] == TOKEN_URL
    data = mock_post.call_args.kwargs["data"]
    assert data == {
        "grant_type": "authorization_code",
        "code": "fake_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "https://example.com/callback",
    }


def test_exchange_code_without_redirect_uri():
    with patch("requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            **{"json.return_value": {}, "raise_for_status.return_value": None}
        )
        _client().exchange_code("fake_code")

    data = mock_post.call_args.kwargs["data"]
    assert "redirect_uri" not in data
    assert data["grant_type"] == "authorization_code"
    assert data["code"] == "fake_code"


# ----------------------------------------------------------------------------------
# refresh_token


def test_refresh_token_posts_refresh_grant():
    token_body = {"access_token": "fake_access2", "refresh_token": "fake_refresh2"}
    with patch("requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            **{"json.return_value": token_body, "raise_for_status.return_value": None}
        )
        result = _client().refresh_token("fake_refresh")

    assert result == token_body
    assert mock_post.call_args.args[0] == TOKEN_URL
    data = mock_post.call_args.kwargs["data"]
    assert data == {
        "grant_type": "refresh_token",
        "refresh_token": "fake_refresh",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }


# ----------------------------------------------------------------------------------
# revoke_token


def test_revoke_token_calls_revoke_endpoint():
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(**{"raise_for_status.return_value": None})
        _client().revoke_token("fake_access")

    assert mock_get.call_args.args[0] == REVOKE_URL
    assert mock_get.call_args.kwargs["params"] == {"access_token": "fake_access"}
    assert mock_get.call_args.kwargs["timeout"] == 60


# ----------------------------------------------------------------------------------
# _token_request error handling


def test_token_request_raises_on_http_error():
    with patch("requests.post") as mock_post:
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("HTTP error")
        mock_post.return_value = resp
        with pytest.raises(Exception, match="HTTP error"):
            _client().exchange_code("fake_code")
