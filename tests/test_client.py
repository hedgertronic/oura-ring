"""Tests for oura_ring.client.OuraClient.

All HTTP is mocked at the requests.Session.request boundary; no live network calls
are made and no real tokens or personal data appear anywhere.
"""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from oura_ring import API_URL, OuraClient

FAKE_TOKEN = "fake_token"


def _response(json_data, status_ok=True):
    """Build a fake requests.Response-like mock."""
    resp = MagicMock()
    resp.json.return_value = json_data
    if status_ok:
        resp.raise_for_status.return_value = None
    else:
        resp.raise_for_status.side_effect = Exception("HTTP error")
    return resp


def _page(data, next_token=None):
    """Build a paginated-envelope payload."""
    return {"data": data, "next_token": next_token}


# ----------------------------------------------------------------------------------
# __init__ / auth header


def test_init_positional_token_sets_header():
    client = OuraClient(FAKE_TOKEN)
    assert client.session.headers["Authorization"] == f"Bearer {FAKE_TOKEN}"


def test_init_keyword_token_sets_header():
    client = OuraClient(personal_access_token=FAKE_TOKEN)
    assert client.session.headers["Authorization"] == f"Bearer {FAKE_TOKEN}"


def test_init_no_token_raises():
    with pytest.raises(ValueError):
        OuraClient()


# ----------------------------------------------------------------------------------
# context manager


def test_context_manager_returns_client_and_closes():
    client = OuraClient(FAKE_TOKEN)
    client.session.close = MagicMock()
    with client as entered:
        assert entered is client
    client.session.close.assert_called_once()


def test_close_closes_session():
    client = OuraClient(FAKE_TOKEN)
    client.session.close = MagicMock()
    client.close()
    client.session.close.assert_called_once()


# ----------------------------------------------------------------------------------
# _format_dates


def test_format_dates_defaults():
    client = OuraClient(FAKE_TOKEN)
    start, end = client._format_dates(None, None)
    today = date.today()
    assert end == str(today)
    assert start == str(today - timedelta(days=1))


def test_format_dates_explicit_passthrough():
    client = OuraClient(FAKE_TOKEN)
    start, end = client._format_dates("2024-01-01", "2024-01-31")
    assert (start, end) == ("2024-01-01", "2024-01-31")


def test_format_dates_start_after_end_raises():
    client = OuraClient(FAKE_TOKEN)
    with pytest.raises(ValueError):
        client._format_dates("2024-02-01", "2024-01-01")


# ----------------------------------------------------------------------------------
# _format_datetimes


def test_format_datetimes_defaults_returns_tuple():
    client = OuraClient(FAKE_TOKEN)
    result = client._format_datetimes(None, None)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(x, str) for x in result)


def test_format_datetimes_mixed_aware_and_naive_does_not_raise():
    """Bug fix: one aware datetime + one naive (defaulted) must not raise TypeError."""
    client = OuraClient(FAKE_TOKEN)
    result = client._format_datetimes("2024-01-01T00:00:00+00:00", None)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_format_datetimes_start_after_end_raises():
    client = OuraClient(FAKE_TOKEN)
    with pytest.raises(ValueError):
        client._format_datetimes(
            "2024-02-01T00:00:00+00:00", "2024-01-01T00:00:00+00:00"
        )


# ----------------------------------------------------------------------------------
# _make_request


def test_make_request_builds_url_and_returns_json():
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response({"ok": True})
        result = client._make_request(method="GET", url_slug="v2/foo/bar")

    assert result == {"ok": True}
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/v2/foo/bar"
    assert kwargs["method"] == "GET"
    assert kwargs["timeout"] == 60


def test_make_request_calls_raise_for_status():
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        resp = _response({}, status_ok=False)
        mock_request.return_value = resp
        with pytest.raises(Exception, match="HTTP error"):
            client._make_request(method="GET", url_slug="v2/foo")
        resp.raise_for_status.assert_called_once()


# ----------------------------------------------------------------------------------
# _make_paginated_request


def test_paginated_request_follows_next_token_and_concatenates():
    client = OuraClient(FAKE_TOKEN)

    captured_params = []
    responses = [
        _response(_page([{"id": "test-id-1"}], next_token="tok-abc")),
        _response(_page([{"id": "test-id-2"}], next_token=None)),
    ]

    def side_effect(*args, **kwargs):
        # Snapshot params at call time; the client mutates the dict in place.
        captured_params.append(dict(kwargs.get("params") or {}))
        return responses[len(captured_params) - 1]

    with patch("requests.Session.request", side_effect=side_effect):
        result = client._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/daily_sleep",
            params={"start_date": "2024-01-01", "end_date": "2024-01-02"},
        )

    assert result == [{"id": "test-id-1"}, {"id": "test-id-2"}]
    assert len(captured_params) == 2
    # First call has no next_token; second carries the token from page 1.
    assert "next_token" not in captured_params[0]
    assert captured_params[1]["next_token"] == "tok-abc"


# ----------------------------------------------------------------------------------
# Date endpoints (list path + document_id path), parametrized.

# (method_name, expected_slug) for endpoints taking start_date/end_date/document_id.
DATE_ENDPOINT_TABLE = [
    ("get_rest_mode_period", "v2/usercollection/rest_mode_period"),
    ("get_sleep_time", "v2/usercollection/sleep_time"),
    ("get_daily_sleep", "v2/usercollection/daily_sleep"),
    ("get_daily_spo2", "v2/usercollection/daily_spo2"),
    ("get_daily_stress", "v2/usercollection/daily_stress"),
    ("get_enhanced_tag", "v2/usercollection/enhanced_tag"),
    ("get_daily_activity", "v2/usercollection/daily_activity"),
    ("get_daily_readiness", "v2/usercollection/daily_readiness"),
    ("get_sleep_periods", "v2/usercollection/sleep"),
    ("get_sessions", "v2/usercollection/session"),
    ("get_tags", "v2/usercollection/tag"),
    ("get_workouts", "v2/usercollection/workout"),
    ("get_daily_resilience", "v2/usercollection/daily_resilience"),
    ("get_daily_cardiovascular_age", "v2/usercollection/daily_cardiovascular_age"),
    ("get_vo2_max", "v2/usercollection/vO2_max"),
]


@pytest.mark.parametrize("method_name,slug", DATE_ENDPOINT_TABLE)
def test_date_endpoint_list_path(method_name, slug):
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(_page([{"id": "test-id-1"}]))
        result = getattr(client, method_name)(
            start_date="2024-01-01", end_date="2024-01-31"
        )

    assert result == [{"id": "test-id-1"}]
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/{slug}"
    assert kwargs["params"] == {"start_date": "2024-01-01", "end_date": "2024-01-31"}


@pytest.mark.parametrize("method_name,slug", DATE_ENDPOINT_TABLE)
def test_date_endpoint_document_id_path(method_name, slug):
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        # Bare object with no "data"/"next_token" envelope; a regression to the
        # paginated path would KeyError here.
        mock_request.return_value = _response({"id": "test-id-1"})
        result = getattr(client, method_name)(document_id="test-id-1")

    assert result == {"id": "test-id-1"}
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/{slug}/test-id-1"
    # document_id path is a single request without date params.
    assert "params" not in kwargs


def test_get_ring_configuration_list_has_no_date_params():
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(_page([{"id": "ring-id-1"}]))
        result = client.get_ring_configuration()

    assert result == [{"id": "ring-id-1"}]
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/v2/usercollection/ring_configuration"
    assert kwargs["params"] == {}


def test_get_ring_configuration_document_id_path():
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response({"id": "ring-id-1"})
        result = client.get_ring_configuration(document_id="ring-id-1")

    assert result == {"id": "ring-id-1"}
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/v2/usercollection/ring_configuration/ring-id-1"
    assert "params" not in kwargs


def test_enhanced_tag_document_id_single_request_no_data_envelope():
    """Bug fix: enhanced_tag with document_id does a single request and does not
    read a "data" envelope."""
    client = OuraClient(FAKE_TOKEN)
    bare = {"id": "test-id-1", "tag_type_code": "string", "comment": "fake"}
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(bare)
        result = client.get_enhanced_tag(document_id="test-id-1")

    assert result == bare
    mock_request.assert_called_once()
    assert (
        mock_request.call_args.kwargs["url"]
        == f"{API_URL}/v2/usercollection/enhanced_tag/test-id-1"
    )


def test_vo2_max_casing_list_and_document_id():
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(_page([{"id": "test-id-1"}]))
        client.get_vo2_max(start_date="2024-01-01", end_date="2024-01-02")
    assert (
        mock_request.call_args.kwargs["url"] == f"{API_URL}/v2/usercollection/vO2_max"
    )

    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response({"id": "test-id-1"})
        client.get_vo2_max(document_id="test-id-1")
    assert (
        mock_request.call_args.kwargs["url"]
        == f"{API_URL}/v2/usercollection/vO2_max/test-id-1"
    )


# ----------------------------------------------------------------------------------
# Datetime endpoints (no document_id path)

DATETIME_ENDPOINT_TABLE = [
    ("get_heart_rate", "v2/usercollection/heartrate"),
    ("get_ring_battery_level", "v2/usercollection/ring_battery_level"),
]


@pytest.mark.parametrize("method_name,slug", DATETIME_ENDPOINT_TABLE)
def test_datetime_endpoint_sends_datetime_params(method_name, slug):
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(_page([{"bpm": 60}]))
        result = getattr(client, method_name)(
            start_datetime="2024-01-01T00:00:00+00:00",
            end_datetime="2024-01-02T00:00:00+00:00",
        )

    assert result == [{"bpm": 60}]
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/{slug}"
    assert set(kwargs["params"].keys()) == {"start_datetime", "end_datetime"}
    # _format_datetimes round-trips through datetime, whose str() uses a space
    # separator rather than 'T'.
    assert kwargs["params"]["start_datetime"] == "2024-01-01 00:00:00+00:00"
    assert kwargs["params"]["end_datetime"] == "2024-01-02 00:00:00+00:00"


@pytest.mark.parametrize("method_name,slug", DATETIME_ENDPOINT_TABLE)
def test_datetime_endpoint_latest_param(method_name, slug):
    client = OuraClient(FAKE_TOKEN)
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(_page([{"timestamp": "2024-01-01"}]))
        result = getattr(client, method_name)(latest=True)

    assert result == [{"timestamp": "2024-01-01"}]
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/{slug}"
    assert kwargs["params"] == {"latest": True}


# ----------------------------------------------------------------------------------
# personal_info


def test_get_personal_info():
    client = OuraClient(FAKE_TOKEN)
    info = {"id": "test-id-1", "biological_sex": "male"}
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = _response(info)
        result = client.get_personal_info()

    assert result == info
    mock_request.assert_called_once()
    kwargs = mock_request.call_args.kwargs
    assert kwargs["url"] == f"{API_URL}/v2/usercollection/personal_info"
    assert "params" not in kwargs
