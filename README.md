# Oura Ring for Python <!-- omit in toc -->

Tools for acquiring and analyzing Oura API data.

[Oura](https://ouraring.com) is a wearable ring for monitoring sleep, activity, and workouts.

## Contents <!-- omit in toc -->

- [Installation](#installation)
- [Getting Started](#getting-started)
- [API Requests](#api-requests)
  - [Get Personal Info](#get-personal-info)
  - [Get Daily Sleep](#get-daily-sleep)
  - [Get Daily Activity](#get-daily-activity)
  - [Get Daily Readiness](#get-daily-readiness)
  - [Get Heart Rate](#get-heart-rate)
  - [Get Sleep Periods](#get-sleep-periods)
  - [Get Sessions](#get-sessions)
  - [Get Tags](#get-tags)
  - [Get Workouts](#get-workouts)
- [Usage With DataFrame](#usage-with-dataframe)

## Installation

The `oura_ring` module can be installed via pip:

`pip install oura-ring`

## Getting Started

In order to use the Oura client, you must first generate a [`personal_access_token`](https://cloud.ouraring.com/personal-access-tokens) for your Oura account.

It is best practice to store this value in a `.env` file:

```bash
# Oura credentials
PERSONAL_ACCESS_TOKEN="<PERSONAL_ACCESS_TOKEN>"
```

You can use [`python-dotenv`](https://github.com/theskumar/python-dotenv) to load the enviroment variables for use in code:

```python
import os
from dotenv import load_dotenv

load_dotenv()

pat = os.getenv("PERSONAL_ACCESS_TOKEN") or ""
```

Once the environment variables are loaded, an `OuraClient` object can created:

```python
# Using a traditional constructor and destructor
import oura_ring as ou

client = ou.OuraClient(pat)

...

del client

# Using a context manager that destructs automatically
with ou.OuraClient(pat) as client:
    ...
```

## API Requests

There are nine different API requests that `OuraClient` can make. Full Oura API v2 documentation can be found on [Oura's website](https://cloud.ouraring.com/v2/docs).

### Get Personal Info

**Method**: `get_personal_info()`

**Payload**: None

**Example Response**:

```python
{
    "age": 31,
    "weight": 74.8,
    "height": 1.8,
    "biological_sex": "male",
    "email": "example@example.com"
}
```

### Get Daily Sleep

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
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
    ],
    "next_token": None
}
```

### Get Daily Activity

**Method**: `get_daily_activity(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
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
    ],
    "next_token": None
}
```

### Get Daily Readiness

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
            "contributors": {
                "activity_balance": 56,
                "body_temperature": 98,
                "hrv_balance": 75,
                "previous_day_activity": null,
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
    ],
    "next_token": None
}
```

### Get Heart Rate

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
            "bpm": 60,
            "source": "sleep",
            "timestamp": "2021-01-01T01:02:03+00:00"
        },
        ...
    ],
    "next_token": None
}
```

### Get Sleep Periods

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
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
                    null,
                    50,
                    46,
                    ...
                ],
                "timestamp": "2022-07-12T01:05:14.000-07:00"
            },
            "hrv": {
                "interval": 300,
                "items": [
                    null,
                    -102,
                    -122,
                    ...
                ],
                "timestamp": "2022-07-12T01:05:14.000-07:00"
            },
            "latency": 540,
            "light_sleep_duration": 18750,
            "low_battery_alert": false,
            "lowest_heart_rate": 48,
            "movement_30_sec": "<long sequence of 1|2|3>",
            "period": 0,
            "readiness_score_delta": 0,
            "rem_sleep_duration": 2280,
            "restless_periods": 415,
            "sleep_phase_5_min": "<long sequence of 1|2|3|4>",
            "sleep_score_delta": 0,
            "time_in_bed": 30000,
            "total_sleep_duration": null,
            "type": "long_sleep"
        },
        ...
    ],
    "next_token": None
}
```

### Get Sessions

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
            "day": "2021-11-12",
            "start_datetime": "2021-11-12T12:32:09-08:00",
            "end_datetime": "2021-11-12T12:40:49-08:00",
            "type": "rest",
            "heart_rate": null,
            "heart_rate_variability": null,
            "mood": null,
            "motion_count": {
                "interval": 5,
                "items": [
                    0
                ],
                "timestamp": "2021-11-12T12:32:09.000-08:00"
            }
        },
        ...
    ],
    "next_token": None
}
```

### Get Tags

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
            "day": "2021-01-01",
            "text": "Need coffee",
            "timestamp": "2021-01-01T01:02:03-08:00",
            "tags": [
                "tag_generic_nocaffeine"
            ]
        },
        ...
    ],
    "next_token": None
}
```

### Get Workouts

**Method**: `get_daily_sleep(start_date: str = <end_date - 1 day>, end_date: str = <today's date>, next_token: str = None)`

**Payload**:

- `start_date`: The earliest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to one day before the `end_date` parameter.
- `end_date`: The latest date for which to get data. Expected in ISO 8601 format (YYYY-MM-DD). Defaults to today's date.
- `next_token`: Optional pagination token.

**Example Response**:

```python
{
    "data": [
        {
            "activity": "cycling",
            "calories": 300,
            "day": "2021-01-01",
            "distance": 13500.5,
            "end_datetime": "2021-01-01T01:00:00.000000+00:00",
            "intensity": "moderate",
            "label": null,
            "source": "manual",
            "start_datetime": "2021-01-01T01:30:00.000000+00:00"
        },
        ...
    ],
    "next_token": None
}
```

## Usage With DataFrame

Using Oura API data with a Pandas DataFrame is very straightforward:

```python
>>> sleep = client.get_daily_sleep()
>>> pd.json_normalize(sleep["data"])

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
>>> pd.json_normalize(readiness["data"])

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
