####################################################################################
# Attributes:
# API_URL (str): Base URL for API requests.

from datetime import date, timedelta
from typing import Any

import requests

API_URL = "https://api.ouraring.com"


class Client:
    """Make requests to the Oura API.

    Attributes:
        session (authlib.OAuth2Session): Requests session for accessing the Oura API.

    Raises:
        ValueError: If `start_date` is after `end_date`.
    """

    ####################################################################################
    # INIT STUFF
    def __init__(self, personal_access_token: str):
        """Initialize a Requests session for making API requests.

        Args:
            personal_access_token (str): Token for accessing the API provided by Oura.
        """
        self._personal_access_token: str = personal_access_token

        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {self._personal_access_token}"}
        )

    def __enter__(self) -> 'Client':
        """Enter a context manager.

        Returns:
            OuraClient: An Oura client with an active Requests session.
        """
        return self

    def __exit__(self, *_) -> None:
        """Exit a context manager by closing the Requests session.

        Args:
            _ (Any): Exception arguments passed when closing context manager.
        """
        self.close()

    def close(self):
        """Close the Requests session."""
        self.session.close()

    ####################################################################################
    # HELPER METHODS
    def _make_paginated_request(
            self, method, url_slug, **kwargs
    ) -> list[dict[str, Any]]:
        params = kwargs.pop("params", {})
        response_data: list[dict[str, Any]] = []

        while True:
            response = self._make_request(
                method=method,
                url_slug=url_slug,
                params=params,
                **kwargs,
            )

            response_data += response["data"]

            if next_token := response["next_token"]:
                params["next_token"] = next_token

            else:
                break

        return response_data

    def _make_request(self, method, url_slug, **kwargs) -> dict[str, Any]:
        response = self.session.request(
            method=method,
            url=f"{API_URL}/{url_slug}",
            timeout=60,
            **kwargs,
        )

        response.raise_for_status()

        return response.json()

    def _format_dates(
            self, start_date: str | None, end_date: str | None
    ) -> tuple[str, str]:
        end = date.fromisoformat(end_date) if end_date else date.today()
        start = (
            date.fromisoformat(start_date) if start_date else end - timedelta(days=1)
        )

        if start > end:
            raise ValueError(f"Start date greater than end date: {start} > {end}")

        return str(start), str(end)