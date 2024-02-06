"""Tools for acquiring and analyzing Oura API data.

Oura is a wearable ring for monitoring sleep, activity, and workouts. Learn more about
Oura at https://ouraring.com.

Oura API v2 documentation can be found at https://cloud.ouraring.com/v2/docs.

Examples:
    Loading environment variables:
        import os
        from dotenv import load_dotenv

        load_dotenv()

        pat = os.getenv("PERSONAL_ACCESS_TOKEN") or ""

    Creating a client:
        from oura_ring import OuraClient

        client = OuraClient(pat)
        ...

        with OuraClient(pat) as client:
            ...

    Making requests:
        client = OuraClient(pat)

        sleep = client.get_daily_sleep()
        activity = client.get_daily_activity()

        print(sleep)
        print(activity)

Attributes:
    API_URL (str): Base URL for API requests.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import requests


API_URL = "https://api.ouraring.com"


class OuraClient:
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

    def __enter__(self) -> OuraClient:
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
    # API ENDPOINTS

    def get_personal_info(self) -> dict[str, Any]:
        """Make request to Get Personal Info endpoint.

        Returns personal info data for the specified Oura user.

        The Personal Info scope includes personal information (e.g. age, email, weight,
        and height) about the user.

        Returns:
            dict[str, list[dict[str, Any]]]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "age": 31,
                        "weight": 74.8,
                        "height": 1.8,
                        "biological_sex": "male",
                        "email": "example@example.com"
                    }
        """
        return self._make_request(
            method="GET", url_slug="v2/usercollection/personal_info"
        )

    def get_rest_mode_period(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
            document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Rest Mode Period endpoint.

        Returns Oura Rest Mode Period data for the specified Oura user within
        a given timeframe.

        The Rest Mode scope includes information about rest mode periods. This
        includes the start, end time and details of the rest mode period.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "end_day": "2019-08-24",
                            "end_time": "2019-08-24T14:15:22Z",
                            "episodes": [
                                {
                                    "tags": [
                                        "string"
                                    ],
                                    "timestamp": "2019-08-24T14:15:22Z"
                                }
                            ],
                            "start_day": "2019-08-24",
                            "start_time": "2019-08-24T14:15:22Z"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "end_day": "2019-08-24",
                        "end_time": "2019-08-24T14:15:22Z",
                        "episodes": [
                            {
                                "tags": [
                                    "string"
                                ],
                                "timestamp": "2019-08-24T14:15:22Z"
                            }
                        ],
                        "start_day": "2019-08-24",
                        "start_time": "2019-08-24T14:15:22Z"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/rest_mode_period/{document_id}"
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/rest_mode_period",
            params={"start_date": start, "end_date": end},
        )

    def get_ring_configuration(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
            document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Ring Configuration endpoint.

        Returns Oura Ring Configuration data for the specified Oura user within
        a given timeframe.

        The Ring Configuration scope includes information about the user's
        ring(s). This includes the model, size, color, etc.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "color": "glossy_black",
                            "design": "heritage",
                            "firmware_version": "string",
                            "hardware_type": "gen1",
                            "set_up_at": "2019-08-24T14:15:22Z",
                            "size": 0
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "color": "glossy_black",
                        "design": "heritage",
                        "firmware_version": "string",
                        "hardware_type": "gen1",
                        "set_up_at": "2019-08-24T14:15:22Z",
                        "size": 0
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/ring_configuration/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/ring_configuration",
            params={"start_date": start, "end_date": end},
        )

    def get_sleep_time(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
            document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Sleep Time endpoint.

        Returns Oura Sleep Time data for the specified Oura user within a given
        timeframe.

        Recommendations for the optimal bedtime window that is calculated based
        on sleep data.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "day": "2019-08-24",
                            "optimal_bedtime": {
                                "day_tz": 0,
                                "end_offset": 0,
                                "start_offset": 0
                            },
                            "recommendation": "improve_efficiency",
                            "status": "not_enough_nights"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "day": "2019-08-24",
                        "optimal_bedtime": {
                            "day_tz": 0,
                            "end_offset": 0,
                            "start_offset": 0
                        },
                        "recommendation": "improve_efficiency",
                        "status": "not_enough_nights"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/sleep_time/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/sleep_time",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_sleep(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Daily Sleep endpoint.

        Returns Oura Daily Sleep data for the specified Oura user within a given
        timeframe.

        A sleep period is a nearly continuous, longish period of time spent lying down
        in bed.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "contributors": {
                                "deep_sleep": 57,
                                "efficiency": 98,
                                "latency": 81,
                                "rem_sleep": 20,
                                "restfulness": 54,
                                "timing": 84,
                                "total_sleep": 60
                            },
                            "day": "2022-07-14",
                            "score": 63,
                            "timestamp": "2022-07-14T00:00:00+00:00"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "contributors": {
                            "deep_sleep": 57,
                            "efficiency": 98,
                            "latency": 81,
                            "rem_sleep": 20,
                            "restfulness": 54,
                            "timing": 84,
                            "total_sleep": 60
                        },
                        "day": "2022-07-14",
                        "score": 63,
                        "timestamp": "2022-07-14T00:00:00+00:00"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/daily_sleep/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/daily_sleep",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_spo2(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
            document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Daily Spo2 endpoint.

        Returns Oura Daily Spo2 data for the specified Oura user within a given
        timeframe.

        The Daily SpO2 (blood oxygenation) routes include daily SpO2 average.
        Data will only be available for users with a Gen 3 Oura Ring.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "day": "2019-08-24",
                            "spo2_percentage": {
                                "average": 0
                            }
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "day": "2019-08-24",
                        "spo2_percentage": {
                            "average": 0
                        }
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/daily_spo2/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/daily_spo2",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_stress(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Daily Stress endpoint.

        Returns Oura Daily Stress data for the specified Oura user within a given
        timeframe.

        The daily stress route includes a summary of the number of minutes the user
        spends in high stress and high recovery each day. This is a great way to
        see how your stress and recovery are trending over time. Stress and
        recovery are mutally exclusive. E.g. one can only be stressed or recovered
        at any given moement - and cannot be stressed and recovered at the same
        time.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "day": "2019-08-24",
                            "stress_high": 0,
                            "recovery_high": 0,
                            "day_summary": "restored"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "day": "2019-08-24",
                        "stress_high": 0,
                        "recovery_high": 0,
                        "day_summary": "restored"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/daily_stress/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/daily_stress",
            params={"start_date": start, "end_date": end},
        )

    def get_enhanced_tag(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Enhanced Tag endpoint.

        Returns Oura Enhanced Tag data for the specified Oura user within a given
        timeframe.

        The Enhanced Tags data scope includes tags that Oura users enter within
        the Oura mobile app. Enhanced Tags can be added for any lifestyle
        choice, habit, mood change, or environmental factor an Oura user wants
        to monitor the effects of. Enhanced Tags also contain context on a
        tag’s start and end time, whether a tag repeats daily, and comments.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "tag_type_code": "string",
                            "start_time": "2019-08-24T14:15:22Z",
                            "end_time": "2019-08-24T14:15:22Z",
                            "start_day": "2019-08-24",
                            "end_day": "2019-08-24",
                            "comment": "string"
                        },
                        ...
                    ]
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_paginated_request(
                method="GET",
                url_slug=f"v2/usercollection/enhanced_tag/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/enhanced_tag",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_activity(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Daily Activity endpoint.

        Returns Oura Daily Activity data for the specified Oura user within a given
        timeframe.

        The Daily Activity scope includes daily activity summary values and detailed
        activity levels. Activity levels are expressed in metabolic equivalent of task
        minutes (MET mins). Oura tracks activity based on the movement.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "class_5_min": "<long sequence of 0|1|2|3|4|5>",
                            "score": 82,
                            "active_calories": 1222,
                            "average_met_minutes": 1.90625,
                            "contributors": {
                                "meet_daily_targets": 43,
                                "move_every_hour": 100,
                                "recovery_time": 100,
                                "stay_active": 98,
                                "training_frequency": 71,
                                "training_volume": 98
                            },
                            "equivalent_walking_distance": 20122,
                            "high_activity_met_minutes": 444,
                            "high_activity_time": 3000,
                            "inactivity_alerts": 0,
                            "low_activity_met_minutes": 117,
                            "low_activity_time": 10020,
                            "medium_activity_met_minutes": 391,
                            "medium_activity_time": 6060,
                            "met": {
                                "interval": 60,
                                "items": [
                                    0.1,
                                    ...
                                ],
                                "timestamp": "2021-11-26T04:00:00.000-08:00"
                            },
                            "meters_to_target": -16200,
                            "non_wear_time": 27480,
                            "resting_time": 18840,
                            "sedentary_met_minutes": 10,
                            "sedentary_time": 21000,
                            "steps": 18430,
                            "target_calories": 350,
                            "target_meters": 7000,
                            "total_calories": 3446,
                            "day": "2021-11-26",
                            "timestamp": "2021-11-26T04:00:00-08:00"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "class_5_min": "<long sequence of 0|1|2|3|4|5>",
                        "score": 82,
                        "active_calories": 1222,
                        "average_met_minutes": 1.90625,
                        "contributors": {
                            "meet_daily_targets": 43,
                            "move_every_hour": 100,
                            "recovery_time": 100,
                            "stay_active": 98,
                            "training_frequency": 71,
                            "training_volume": 98
                        },
                        "equivalent_walking_distance": 20122,
                        "high_activity_met_minutes": 444,
                        "high_activity_time": 3000,
                        "inactivity_alerts": 0,
                        "low_activity_met_minutes": 117,
                        "low_activity_time": 10020,
                        "medium_activity_met_minutes": 391,
                        "medium_activity_time": 6060,
                        "met": {
                            "interval": 60,
                            "items": [
                                0.1,
                                ...
                            ],
                            "timestamp": "2021-11-26T04:00:00.000-08:00"
                        },
                        "meters_to_target": -16200,
                        "non_wear_time": 27480,
                        "resting_time": 18840,
                        "sedentary_met_minutes": 10,
                        "sedentary_time": 21000,
                        "steps": 18430,
                        "target_calories": 350,
                        "target_meters": 7000,
                        "total_calories": 3446,
                        "day": "2021-11-26",
                        "timestamp": "2021-11-26T04:00:00-08:00"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/daily_activity/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/daily_activity",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_readiness(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Daily Readiness endpoint.

        Returns Oura Daily Readiness data for the specified Oura user within a given
        timeframe.

        Readiness tells how ready you are for the day.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "contributors": {
                                "activity_balance": 56,
                                "body_temperature": 98,
                                "hrv_balance": 75,
                                "previous_day_activity": None,
                                "previous_night": 35,
                                "recovery_index": 47,
                                "resting_heart_rate": 94,
                                "sleep_balance": 73
                            },
                            "day": "2021-10-27",
                            "score": 66,
                            "temperature_deviation": -0.2,
                            "temperature_trend_deviation": 0.1,
                            "timestamp": "2021-10-27T00:00:00+00:00"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "contributors": {
                            "activity_balance": 56,
                            "body_temperature": 98,
                            "hrv_balance": 75,
                            "previous_day_activity": None,
                            "previous_night": 35,
                            "recovery_index": 47,
                            "resting_heart_rate": 94,
                            "sleep_balance": 73
                        },
                        "day": "2021-10-27",
                        "score": 66,
                        "temperature_deviation": -0.2,
                        "temperature_trend_deviation": 0.1,
                        "timestamp": "2021-10-27T00:00:00+00:00"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/daily_readiness/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/daily_readiness",
            params={"start_date": start, "end_date": end},
        )

    def get_heart_rate(
        self,
        start_datetime: str | None = None,
        end_datetime: str | None = None,
    ) -> list[dict[str, Any]]:
        """Make request to Get Heart Rate endpoint.

        Returns available heart rate data for a specified Oura user within a given
        timeframe.

        The Heart Rate data scope includes time-series heart rate data throughout the
        day and night. Heart rate is provided at 5-minute increments. For heart rate
        data recorded from a Session, see Sessions endpoint.

        Args:
            start_datetime (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DDThh:mm:ss`). Time is optional,
                will default to 00:00:00. Time zone is also supported. Defaults to
                one day before `end_date`.
            end_datetime (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DDThh:mm:ss`). Time is optional, will
                default to 00:00:00. Time zone is also supported. Defaults to today's
                date.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "bpm": 60,
                            "source": "sleep",
                            "timestamp": "2021-01-01T01:02:03+00:00"
                        },
                        ...
                    ]
        """
        start, end = self._format_datetimes(start_datetime, end_datetime)

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/heartrate",
            params={"start_datetime": start, "end_datetime": end},
        )

    def get_sleep_periods(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Sleep Periods endpoint.

        Returns available Oura sleep data for the specified Oura user within a given
        timeframe.

        Returns Oura Sleep data for the specified Oura user within a given timeframe. A
        user can have multiple sleep periods per day.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "average_breath": 12.625,
                            "average_heart_rate": 4.25,
                            "average_hrv": 117,
                            "awake_time": 4800,
                            "bedtime_end": "2022-07-12T09:25:14-07:00",
                            "bedtime_start": "2022-07-12T01:05:14-07:00",
                            "day": "2022-07-12",
                            "deep_sleep_duration": 4170,
                            "efficiency": 84,
                            "heart_rate": {
                                "interval": 300,
                                "items": [
                                    None,
                                    50,
                                    46,
                                    ...
                                ],
                                "timestamp": "2022-07-12T01:05:14.000-07:00"
                            },
                            "hrv": {
                                "interval": 300,
                                "items": [
                                    None,
                                    -102,
                                    -122,
                                    ...
                                ],
                                "timestamp": "2022-07-12T01:05:14.000-07:00"
                            },
                            "latency": 540,
                            "light_sleep_duration": 18750,
                            "low_battery_alert": False,
                            "lowest_heart_rate": 48,
                            "movement_30_sec": "<long sequence of 1|2|3>",
                            "period": 0,
                            "readiness_score_delta": 0,
                            "rem_sleep_duration": 2280,
                            "restless_periods": 415,
                            "sleep_phase_5_min": "<long sequence of 1|2|3|4>",
                            "sleep_score_delta": 0,
                            "time_in_bed": 30000,
                            "total_sleep_duration": None,
                            "type": "long_sleep"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "average_breath": 12.625,
                        "average_heart_rate": 4.25,
                        "average_hrv": 117,
                        "awake_time": 4800,
                        "bedtime_end": "2022-07-12T09:25:14-07:00",
                        "bedtime_start": "2022-07-12T01:05:14-07:00",
                        "day": "2022-07-12",
                        "deep_sleep_duration": 4170,
                        "efficiency": 84,
                        "heart_rate": {
                            "interval": 300,
                            "items": [
                                None,
                                50,
                                46,
                                ...
                            ],
                            "timestamp": "2022-07-12T01:05:14.000-07:00"
                        },
                        "hrv": {
                            "interval": 300,
                            "items": [
                                None,
                                -102,
                                -122,
                                ...
                            ],
                            "timestamp": "2022-07-12T01:05:14.000-07:00"
                        },
                        "latency": 540,
                        "light_sleep_duration": 18750,
                        "low_battery_alert": False,
                        "lowest_heart_rate": 48,
                        "movement_30_sec": "<long sequence of 1|2|3>",
                        "period": 0,
                        "readiness_score_delta": 0,
                        "rem_sleep_duration": 2280,
                        "restless_periods": 415,
                        "sleep_phase_5_min": "<long sequence of 1|2|3|4>",
                        "sleep_score_delta": 0,
                        "time_in_bed": 30000,
                        "total_sleep_duration": None,
                        "type": "long_sleep"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/sleep/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/sleep",
            params={"start_date": start, "end_date": end},
        )

    def get_sessions(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Sessions endpoint.

        Returns available Oura session data for the specified Oura user within a given
        timeframe.

        The Sessions data scope provides information on how users engage with guided
        and unguided sessions in the Oura app, including the user’s biometric trends
        during the sessions.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "day": "2021-11-12",
                            "start_datetime": "2021-11-12T12:32:09-08:00",
                            "end_datetime": "2021-11-12T12:40:49-08:00",
                            "type": "rest",
                            "heart_rate": None,
                            "heart_rate_variability": None,
                            "mood": None,
                            "motion_count": {
                                "interval": 5,
                                "items": [
                                    0
                                ],
                                "timestamp": "2021-11-12T12:32:09.000-08:00"
                            }
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "day": "2021-11-12",
                        "start_datetime": "2021-11-12T12:32:09-08:00",
                        "end_datetime": "2021-11-12T12:40:49-08:00",
                        "type": "rest",
                        "heart_rate": None,
                        "heart_rate_variability": None,
                        "mood": None,
                        "motion_count": {
                            "interval": 5,
                            "items": [
                                0
                            ],
                            "timestamp": "2021-11-12T12:32:09.000-08:00"
                        }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/session/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/session",
            params={"start_date": start, "end_date": end},
        )

    def get_tags(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Tags endpoint.

        Returns Oura tags data for the specified Oura user within a given timeframe.

        Note: Tag is deprecated. We recommend transitioning to Enhanced Tag.

        The Tags data scope includes tags that Oura users enter within the Oura mobile
        app. Tags are a growing list of activities, environment factors, symptoms,
        emotions, and other aspects that provide broader context into what’s happening
        with users beyond the objective data generated by the Oura Ring.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "day": "2021-01-01",
                            "text": "Need coffee",
                            "timestamp": "2021-01-01T01:02:03-08:00",
                            "tags": [
                                "tag_generic_nocaffeine"
                            ]
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "day": "2021-01-01",
                        "text": "Need coffee",
                        "timestamp": "2021-01-01T01:02:03-08:00",
                        "tags": [
                            "tag_generic_nocaffeine"
                        ]
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/tag/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/tag",
            params={"start_date": start, "end_date": end},
        )

    def get_workouts(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        document_id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Make request to Get Workouts endpoint.

        Returns available Oura workout data for the specified Oura user within a given
        timeframe.

        The Workout data scope includes information about user workouts. This is a
        diverse, growing list of workouts that help inform how the user is training and
        exercising.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.
            document_id (str, options): Individual document id, listed at "id"
                in responses.  Allows you to re-access a previous datapoint.
                If present, start_date and end_date are ignored.

        Returns:
            list[dict[str, Any]]: Response JSON data loaded into an object.
                Example:
                    [
                        {
                            "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                            "activity": "cycling",
                            "calories": 300,
                            "day": "2021-01-01",
                            "distance": 13500.5,
                            "end_datetime": "2021-01-01T01:00:00.000000+00:00",
                            "intensity": "moderate",
                            "label": None,
                            "source": "manual",
                            "start_datetime": "2021-01-01T01:30:00.000000+00:00"
                        },
                        ...
                    ]

            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
                        "activity": "cycling",
                        "calories": 300,
                        "day": "2021-01-01",
                        "distance": 13500.5,
                        "end_datetime": "2021-01-01T01:00:00.000000+00:00",
                        "intensity": "moderate",
                        "label": None,
                        "source": "manual",
                        "start_datetime": "2021-01-01T01:30:00.000000+00:00"
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        if document_id:
            return self._make_request(
                method="GET",
                url_slug=f"v2/usercollection/workout/{document_id}",
            )

        return self._make_paginated_request(
            method="GET",
            url_slug="v2/usercollection/workout",
            params={"start_date": start, "end_date": end},
        )

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

    def _format_datetimes(
        self, start_datetime: str | None, end_datetime: str | None
    ) -> tuple[str, str]:
        end = datetime.fromisoformat(end_datetime) if end_datetime else datetime.today()
        start = (
            datetime.fromisoformat(start_datetime) if start_datetime else end - timedelta(days=1)
        )

        if start > end:
            raise ValueError(f"Start datetime greater than end datetime: {start} > {end}")

        return str(start), str(end)
