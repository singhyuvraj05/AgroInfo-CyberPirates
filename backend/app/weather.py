import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class WeatherServiceError(RuntimeError):
    pass


def get_weather(latitude: float, longitude: float) -> dict:
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation",
            "daily": "precipitation_sum,precipitation_probability_max",
            "forecast_days": 3,
            "timezone": "auto",
        }
    )
    request = Request(
        f"https://api.open-meteo.com/v1/forecast?{query}",
        headers={"Accept": "application/json"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            if response.status != 200:
                raise WeatherServiceError(
                    f"Open-Meteo returned HTTP {response.status}"
                )
            return json.load(response)
    except WeatherServiceError:
        raise
    except Exception as error:
        raise WeatherServiceError("Unable to retrieve weather from Open-Meteo") from error
