"""Tools for acquiring and analyzing Oura API data.

Oura is a wearable ring for monitoring sleep, activity, and workouts. Learn more about
Oura at https://ouraring.com.

Oura API v1 documentation can be found at https://cloud.ouraring.com/docs

API V1 Deprecation
The current timeline to sunset the Oura API V1 is January 22nd, 2024. However as of
the time of the writing of this library, there is still functionality that has not
been ported to the v2 API

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

from client import Client
from typing import Any


class OuraClient(Client):
    ####################################################################################
    # API ENDPOINTS

    def get_personal_info(self) -> dict[str, Any]:
        """Make request to Get Personal Info endpoint.

        Returns personal info data for the specified Oura user.

        The Personal Info scope includes personal information (e.g. age, email, weight,
        and height) about the user.

        Returns:
            dict[str, Any]: Response JSON data loaded into an object.
                Example:
                    {
                        "age": 46,
                        "weight": 102.2,
                        "height": 190,
                        "gender": "male",
                        "email": "example@example.com"
                    }
        """
        return self._make_request(
            method="GET", url_slug="v1/userinfo"
        )

    def get_daily_sleep(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
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

        Returns:
            dict[str, list[dict[str, Any]]]: Response JSON data loaded into an object.
                Example:
                    {
                        'sleep': [
                            {
                                'summary_date': '2024-01-09',
                                'period_id': 1,
                                'is_longest': 1,
                                'timezone': -360,
                                'bedtime_end': '2024-01-10T07:33:10-06:00',
                                'bedtime_start': '2024-01-10T00:04:10-06:00',
                                'type': 'long_sleep',
                                'breath_average': 12.125,
                                'average_breath_variation': 4.375,
                                'duration': 26940,
                                'total': 22650,
                                'awake': 4290,
                                'rem': 4470,
                                'deep': 6240,
                                'light': 11940,
                                'midpoint_time': 13200,
                                'efficiency': 84,
                                'restless': 6,
                                'onset_latency': 180,
                                'got_up_count': 1,
                                'wake_up_count': 8,
                                'hr_5min': [0, 68, ...],
                                'hr_average': 59.524,
                                'hr_lowest': 53.0,
                                'lowest_heart_rate_time_offset': 9810,
                                'hypnogram_5min': '421111122333221111244221133322222212222242111224444333223344221112224222322222213222211444',
                                'rmssd': 65,
                                'rmssd_5min': [0, 43, ...],
                                'score': 73,
                                'score_alignment': 78,
                                'score_deep': 97,
                                'score_disturbances': 59,
                                'score_efficiency': 81,
                                'score_latency': 67,
                                'score_rem': 71,
                                'score_total': 70,
                                'temperature_deviation': -0.4,
                                'temperature_trend_deviation': -0.03,
                                'bedtime_start_delta': 250,
                                'bedtime_end_delta': 27190,
                                'midpoint_at_delta': 13450,
                                'temperature_delta': -0.4
                            },
                            ...
                        ]
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_request(
            method="GET",
            url_slug="v1/sleep",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_activity(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
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

        Returns:
            dict[str, list[dict[str, Any]]]: Response JSON data loaded into an object.
                Example:
                    {
                        'activity': [
                            {
                                'summary_date': '2024-01-09',
                                'timezone': -360,
                                'day_start': '2024-01-09T04:00:00-06:00',
                                'day_end': '2024-01-10T03:59:59-06:00',
                                'cal_active': 547,
                                'cal_total': 3019,
                                'class_5min': '211111111111111111111111112211111111212320000000000000000033333333343343422222222222222222222222233334333333432222222222222223332222222222223222223222232222223333332223333333334323232333322223222220000000000000003332233222212223333432222233211111111111111111122111111111111111111122111111',
                                'steps': 9915,
                                'daily_movement': 9469,
                                'non_wear': 160,
                                'rest': 432,
                                'inactive': 510,
                                'low': 310,
                                'medium': 28,
                                'high': 0,
                                'inactivity_alerts': 2,
                                'average_met': 1.5,
                                'met_1min': [1.2, 1.3, ...],
                                'met_min_inactive': 10,
                                'met_min_low': 284,
                                'met_min_medium': 94,
                                'met_min_high': 0,
                                'target_calories': 500,
                                'target_km': 9.0,
                                'target_miles': 5.592339,
                                'to_target_km': -0.6,
                                'to_target_miles': -0.3728226,
                                'score': 77,
                                'score_meet_daily_targets': 95,
                                'score_move_every_hour': 78,
                                'score_recovery_time': 100,
                                'score_stay_active': 79,
                                'score_training_frequency': 1,
                                'score_training_volume': 61,
                                'rest_mode_state': 0,
                                'total': 338
                            },
                            ...
                        ]
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_request(
            method="GET",
            url_slug="v1/activity",
            params={"start_date": start, "end_date": end},
        )

    def get_daily_readiness(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
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

        Returns:
            dict[str, list[dict[str, Any]]]: Response JSON data loaded into an object.
                Example:
                    {
                        'readiness': [
                            {
                                'summary_date': '2024-01-09',
                                'score': 84,
                                'score_activity_balance': 87,
                                'score_hrv_balance': 84,
                                'score_previous_day': 78,
                                'score_previous_night': 67,
                                'score_recovery_index': 97,
                                'score_resting_hr': 96,
                                'score_sleep_balance': 82,
                                'score_temperature': 91,
                                'rest_mode_state': 0,
                                'period_id': 1
                            },
                            ...
                        ]
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_request(
            method="GET",
            url_slug="v1/readiness",
            params={"start_date": start, "end_date": end},
        )
    def get_daily_ideal_bedtime(
            self,
            start_date: str | None = None,
            end_date: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Make request to Get Ideal Bedtime endpoint.

        Returns Oura Ideal Bedtime data for the specified Oura user within a
        given timeframe.

        Ideal bedtime is an optimal bedtime window that is calculated based on your sleep data.

        Args:
            start_date (str, optional): The earliest date for which to get data.
                Expected in ISO 8601 format (`YYYY-MM-DD`). Defaults to one day
                before `end_date`.
            end_date (str, optional): The latest date for which to get data. Expected
                in ISO 8601 format (`YYYY-MM-DD`). Defaults to today's date.

        Returns:
            dict[str, list[dict[str, Any]]]: Response JSON data loaded into an object.
                Example:
                    {
                        'ideal_bedtimes': [
                            {
                                'date': '2024-01-09',
                                'bedtime_window': {
                                    'start': -4500,
                                    'end': -900
                                },
                                'status': 'IDEAL_BEDTIME_AVAILABLE'
                            },
                            ...
                        ]
                    }
        """
        start, end = self._format_dates(start_date, end_date)

        return self._make_request(
            method="GET",
            url_slug="v1/bedtime",
            params={"start_date": start, "end_date": end},
        )
