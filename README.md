# Oura Ring for Python <!-- omit in toc -->

Tools for acquiring and analyzing Oura API data.

[Oura](https://ouraring.com) is a wearable ring for monitoring sleep, activity, and workouts.

## Contents <!-- omit in toc -->

- [Installation](#installation)
- [Getting Started](#getting-started)
- [API Requests](#api-requests)
  - [Get Personal Info](#get-personal-info)
  - [Get Daily Sleep](#get-daily-sleep)
  - [Get Daily SpO2](#get-daily-spo2)
  - [Get Daily Stress](#get-daily-stress)
  - [Get Daily Activity](#get-daily-activity)
  - [Get Daily Readiness](#get-daily-readiness)
  - [Get Daily Resilience](#get-daily-resilience)
  - [Get Daily Cardiovascular Age](#get-daily-cardiovascular-age)
  - [Get VO2 Max](#get-vo2-max)
  - [Get Enhanced Tag](#get-enhanced-tag)
  - [Get Heart Rate](#get-heart-rate)
  - [Get Ring Battery Level](#get-ring-battery-level)
  - [Get Ring Configuration](#get-ring-configuration)
  - [Get Rest Mode Period](#get-rest-mode-period)
  - [Get Sleep Periods](#get-sleep-periods)
  - [Get Sleep Time](#get-sleep-time)
  - [Get Sessions](#get-sessions)
  - [Get Tags](#get-tags)
  - [Get Workouts](#get-workouts)
- [Usage With DataFrame](#usage-with-dataframe)

## Installation

The `oura_ring` module can be installed via pip:

`pip install oura-ring`

Or, using [`uv`](https://github.com/astral-sh/uv):

`uv add oura-ring`

## Getting Started

> **Note**: Personal access tokens were deprecated by Oura in December 2025 — new ones can no longer be created, though previously-issued tokens may still work. New integrations must use OAuth2.

### OAuth2 (recommended)

Create an application in [Oura's developer portal](https://developer.ouraring.com) to obtain a `client_id` and `client_secret`. Use `OuraAuth` to run the Authorization Code flow:

```python
from oura_ring import OuraClient, OuraAuth

oauth = OuraAuth(client_id, client_secret)

# 1. Send the user to the authorization URL to grant access.
url = oauth.authorize_url(
    redirect_uri="https://yourapp.com/callback",
    state="<opaque CSRF value>",
)
# redirect the user to `url`...

# 2. Oura redirects back to your callback with a `?code=...` query param.
#    Exchange that code for tokens.
tokens = oauth.exchange_code(code, redirect_uri="https://yourapp.com/callback")

# 3. Create a client with the access token.
client = OuraClient(access_token=tokens["access_token"])
```

When the access token expires, refresh it with the refresh token:

```python
tokens = oauth.refresh_token(tokens["refresh_token"])
```

> **Important**: Refresh tokens are **single-use**. The refresh response returns a new `refresh_token` that you must persist — the old one is invalidated, so the next refresh will fail if you don't store the new value.

#### Refreshing on demand

The client does not refresh automatically — it raises `requests.HTTPError` when a token has expired (HTTP 401). Catch that, refresh, persist the rotated tokens, and retry. A long-lived service looks roughly like this:

```python
import requests
from oura_ring import OuraClient, OuraAuth

oauth = OuraAuth(client_id, client_secret)

def refresh_and_persist(tokens: dict) -> dict:
    tokens = oauth.refresh_token(tokens["refresh_token"])
    save_tokens(tokens)  # your storage — both access_token AND the new refresh_token
    return tokens

tokens = load_tokens()  # your storage
try:
    sleep = OuraClient(access_token=tokens["access_token"]).get_daily_sleep(...)
except requests.HTTPError as err:
    if err.response.status_code != 401:
        raise
    tokens = refresh_and_persist(tokens)
    sleep = OuraClient(access_token=tokens["access_token"]).get_daily_sleep(...)
```

Persisting the *new* `refresh_token` is the part that bites people: skip it and the next refresh fails with a `400`, because Oura invalidated the old one the moment it issued the replacement.

### Constructing a client from a token

`OuraClient` authenticates every request with a bearer token. That token can be an OAuth2 access token or a legacy personal access token, passed either by keyword or positionally:

```python
from oura_ring import OuraClient

# OAuth2 access token (keyword)
client = OuraClient(access_token=token)

# Positionally — a legacy personal access token still works here for
# backwards compatibility.
client = OuraClient(token)

# Using a context manager
with OuraClient(token) as client:
    ...
```

### Loading a token from the environment

It is best practice to store the token in a `.env` file. The value can be an OAuth2 access token or a legacy personal access token:

```bash
# Oura credentials
OURA_ACCESS_TOKEN="<ACCESS_TOKEN>"
```

You can use [`python-dotenv`](https://github.com/theskumar/python-dotenv) to load the environment variables for use in code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("OURA_ACCESS_TOKEN") or ""

client = OuraClient(token)
```

## API Requests

There are 19 different API requests that `OuraClient` can make. Full Oura API v2 documentation can be found on [Oura's website](https://cloud.ouraring.com/v2/docs).

> **Scope and limitations (by design):** the client returns the API's JSON as-is and raises on HTTP errors (including expired tokens and `429` rate limits) — there is no automatic token refresh or retry built in; use `OuraAuth.refresh_token` to rotate tokens. The optional `fields` (sparse fieldsets) and `latest` query params, and the webhook subscription API, are intentionally not exposed.

### Get Personal Info

**Method**: `get_personal_info()`

**Payload**: None

**Example Response**:

```python
{
    "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
    "age": 31,
    "weight": 74.8,
    "height": 1.8,
    "biological_sex": "male",
    "email": "example@example.com"
}
```

### Get Daily Sleep

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Daily Activity

**Method**: `get_daily_activity(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Daily Readiness

**Method**: `get_daily_readiness(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Daily Resilience

**Method**: `get_daily_resilience(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
[
    {
        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
        "day": "2021-10-27",
        "contributors": {
            "sleep_recovery": 64.2,
            "daytime_recovery": 56.8,
            "stress": 40.1
        },
        "level": "solid"
    },
    ...
]
```

### Get Daily Cardiovascular Age

**Method**: `get_daily_cardiovascular_age(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
[
    {
        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
        "day": "2021-10-27",
        "vascular_age": 32,
        "pulse_wave_velocity": 7.2
    },
    ...
]
```

### Get VO2 Max

**Method**: `get_vo2_max(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
[
    {
        "id": "8f9a5221-639e-4a85-81cb-4065ef23f979",
        "day": "2021-10-27",
        "timestamp": "2021-10-27T00:00:00+00:00",
        "vo2_max": 48
    },
    ...
]
```

### Get Enhanced Tag

**Method**: `get_enhanced_tag(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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

```

### Get Heart Rate

**Method**: `get_heart_rate(start_datetime: str = <end_datetime - 1 day>, end_datetime: str = <now>)`

**Payload**:

- `start_datetime`: The earliest datetime for which to get data. Expected in ISO 8601 format (YYYY-MM-DDThh:mm:ss). Defaults to one day before the `end_datetime` parameter.
- `end_datetime`: The latest datetime for which to get data. Expected in ISO 8601 format (YYYY-MM-DDThh:mm:ss). Defaults to now.

**Example Response**:

```python
[
    {
        "bpm": 60,
        "source": "sleep",
        "timestamp": "2021-01-01T01:02:03+00:00"
    },
    ...
]
```

### Get Ring Battery Level

**Method**: `get_ring_battery_level(start_datetime: str = <end_datetime - 1 day>, end_datetime: str = <now>)`

**Payload**:

- `start_datetime`: The earliest datetime for which to get data. Expected in ISO 8601 format (YYYY-MM-DDThh:mm:ss). Defaults to one day before the `end_datetime` parameter.
- `end_datetime`: The latest datetime for which to get data. Expected in ISO 8601 format (YYYY-MM-DDThh:mm:ss). Defaults to now.

**Example Response**:

```python
[
    {
        "battery_level": 87,
        "timestamp": "2021-01-01T01:02:03+00:00"
    },
    ...
]
```

### Get Sleep Periods

**Method**: `get_sleep_periods(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Sleep Time

**Method**: `get_sleep_time(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Ring Configuration

**Method**: `get_ring_configuration(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Rest Mode Period

**Method**: `get_rest_mode_period(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Sessions

**Method**: `get_sessions(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Daily SpO2

**Method**: `get_daily_spo2(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Daily Stress

**Method**: `get_daily_stress(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Tags

**Method**: `get_tags(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

### Get Workouts

**Method**: `get_workouts(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, document_id: str | None = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.

**Example Response**:

```python
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
```

## Usage With DataFrame

Using Oura API data with a Pandas DataFrame is very straightforward:

```python
>>> import pandas as pd

>>> sleep = client.get_daily_sleep()
>>> pd.json_normalize(sleep)

          day  score                  timestamp  contributors.deep_sleep  \
0  2022-09-01     76  2022-09-01T00:00:00+00:00                       99
1  2022-09-02     81  2022-09-02T00:00:00+00:00                      100

   contributors.efficiency  contributors.latency  contributors.rem_sleep  \
0                       90                    99                      79
1                       88                    75                      95

   contributors.restfulness  contributors.timing  contributors.total_sleep
0                        55                   15                        85
1                        56                   28                        96

[2 rows x 10 columns]

>>> readiness = client.get_daily_readiness()
>>> pd.json_normalize(readiness)

          day  score  temperature_deviation  temperature_trend_deviation  \
0  2022-09-01     87                  -0.09                         0.24
1  2022-09-02     91                  -0.03                         0.11

                   timestamp  contributors.activity_balance  \
0  2022-09-01T00:00:00+00:00                             80
1  2022-09-02T00:00:00+00:00                             86

   contributors.body_temperature  contributors.hrv_balance  \
0                            100                        84
1                            100                        85

  contributors.previous_day_activity  contributors.previous_night  \
0                               None                           75
1                               None                           88

   contributors.recovery_index  contributors.resting_heart_rate  \
0                          100                              100
1                           94                               98

   contributors.sleep_balance
0                          87
1                          93

[2 rows x 13 columns]
```
