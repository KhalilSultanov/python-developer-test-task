import pandas as pd
from fastapi import HTTPException
import requests_cache
from retry_requests import retry
import openmeteo_requests

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


async def fetch_weather_data(latitude: float, longitude: float) -> dict:
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "surface_pressure", "wind_speed_10m"],
            "timezone": "GMT"
        }
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        response = responses[0]
        current_weather = response.Current()
        return {
            "temperature_2m": current_weather.Variables(0).Value(),
            "surface_pressure": current_weather.Variables(1).Value(),
            "wind_speed_10m": current_weather.Variables(2).Value(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")


async def get_weather_by_hour(
        latitude: float,
        longitude: float,
        hour_str: str,
        hourly_params_list: list[str]
) -> dict:
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": hourly_params_list,
            "timezone": "auto"
        }
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        response = responses[0]

        hourly = response.Hourly()
        time_series = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )

        requested_time = pd.Timestamp(hour_str, tz="UTC")

        if requested_time not in time_series:
            raise HTTPException(
                status_code=404,
                detail=f"Данные для времени {hour_str} не найдены (не попало в прогноз)."
            )

        time_index = time_series.get_loc(requested_time)

        weather_data = {}
        for i, param in enumerate(hourly_params_list):
            variable = hourly.Variables(i)
            if not variable:
                weather_data[param] = None
            else:
                arr = variable.ValuesAsNumpy()
                try:
                    weather_data[param] = float(arr[time_index])
                except Exception as e:
                    weather_data[param] = f"Ошибка извлечения данных: {str(e)}"

        return weather_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе погоды за час: {e}")
