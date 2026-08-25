"""Download historical Michigan weather data from Open-Meteo."""

from pathlib import Path


import pandas as pd 


from src.apis.openmeteo_api import (
    get_historical_weather
)


START_DATE = pd.Timestamp("2015-12-31")
END_DATE = pd.Timestamp("2023-04-01")

WEATHER_RAW_DIR  = Path("data/raw/historical_weather")

LOCATIONS = [
    {"city": "Detroit", "latitude": 42.3314, "longitude": -83.0458},
    {"city": "Ann Arbor", "latitude": 42.2808, "longitude": -83.7430},
    {"city": "Lansing", "latitude": 42.7325, "longitude": -84.5555},
    {"city": "Grand Rapids", "latitude": 42.9634, "longitude": -85.6681},
    {"city": "Flint", "latitude": 43.0125, "longitude": -83.6875},
    {"city": "Kalamazoo", "latitude": 42.2917, "longitude": -85.5872},
    {"city": "Traverse City", "latitude": 44.7631, "longitude": -85.6206},
    {"city": "Marquette", "latitude": 46.5436, "longitude": -87.3954},
    {"city": "Sault Ste. Marie", "latitude": 46.4953, "longitude": -84.3453},
    {"city": "Mount Pleasant", "latitude": 43.5978, "longitude": -84.7675},
    {"city": "St. Johns", "latitude": 43.0006, "longitude": -84.5590},
    {"city": "Ionia", "latitude": 42.8722, "longitude": -84.8986},
    {"city": "Bad Axe", "latitude": 43.8014, "longitude": -83.0008},
    {"city": "Saginaw", "latitude": 43.4195, "longitude": -83.9508},
    {"city": "Bay City", "latitude": 43.5945, "longitude": -83.8889},
    {"city": "Manistee", "latitude": 44.0974, "longitude": -86.2044},
    {"city": "Grand Haven", "latitude": 43.0631, "longitude": -86.2284},
    {"city": "Iron Mountain", "latitude": 45.8203, "longitude": -88.0659},
    {"city": "Charlevoix", "latitude": 45.9731, "longitude": -85.1973},
    {"city": "Cheboygan", "latitude": 45.7875, "longitude": -84.7272},
    {"city": "Holland", "latitude": 43.7223, "longitude": -86.1056},
    {"city": "Big Rapids", "latitude": 43.9553, "longitude": -85.4839},
    {"city": "Petoskey", "latitude": 45.3733, "longitude": -84.9553},
    {"city": "Jackson", "latitude": 43.2917, "longitude": -84.4014},
    {"city": "Gaylord", "latitude": 44.6610, "longitude": -84.7147},
    {"city": "Ironwood", "latitude": 46.7867, "longitude": -90.1710},
    {"city": "Escanaba", "latitude": 46.4110, "longitude": -86.6345},
    {"city": "Mackinaw City", "latitude": 45.0275, "longitude": -84.7278},
]

latitudes = [location["latitude"] for location in LOCATIONS]
longitudes = [location["longitude"] for location in LOCATIONS]

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "pressure_msl",
    "wind_speed_10m",
    "precipitation",
    "weather_code",
    "wind_direction_10m",
]

def month_file_is_valid(path, start_date, end_date):
    """Check that a monthly weather file appears complete."""
    if not path.exists():
        return False

    try:
        df = pd.read_csv(path)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return False

    expected_columns = {
        "time",
        "city",
        "latitude",
        "longitude",
        *HOURLY_VARIABLES,
    }

    expected_rows = (
        (end_date - start_date).days + 1
        ) * 24 * len(LOCATIONS)

    return (
        not df.empty
        and expected_columns.issubset(df.columns)
        and len(df) == expected_rows
    )

def main():
    try:
        WEATHER_RAW_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating weather data directory: {e}")
        raise


    current_start = START_DATE


    while current_start <= END_DATE:
        current_end = min(
            current_start + pd.offsets.MonthEnd(0),
            END_DATE
        )

        filename = (
            f"mi_hourly_weather_{current_start.strftime('%Y-%m')}.csv"
        )

        month_path = WEATHER_RAW_DIR / filename

        if month_file_is_valid(month_path, current_start, current_end):
            print(f"Skipping {filename}: already downloaded")
            current_start = current_end + pd.Timedelta(days=1)
            continue

        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "start_date": current_start.strftime("%Y-%m-%d"),
            "end_date": current_end.strftime("%Y-%m-%d"),
            "hourly": HOURLY_VARIABLES,
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "GMT",
            "models": "era5",
        }

        print(f"Requesting {current_start.date()} to {current_end.date()}")

        responses = get_historical_weather(params)

        if len(responses) != len(LOCATIONS):
            raise ValueError(
                f"Expected {len(LOCATIONS)} responses, "
                f"but received {len(responses)}."
            )

        month_dfs = []

        for location, response in zip(LOCATIONS, responses):
            hourly = response.Hourly()

            weather_columns = {}

            for i in range(len(HOURLY_VARIABLES)):
                weather_columns[HOURLY_VARIABLES[i]] = hourly.Variables(i).ValuesAsNumpy()

            timestamps = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )

            city_df = pd.DataFrame(weather_columns)

            city_df.insert(0, "longitude", location["longitude"])
            city_df.insert(0, "latitude", location["latitude"])
            city_df.insert(0, "city", location["city"])
            city_df.insert(0, "time", timestamps)

            month_dfs.append(city_df)

        month_df = pd.concat(month_dfs, ignore_index=True)

        month_df.to_csv(month_path, index=False)

        print(f"Saved {month_path}")

        current_start = current_end + pd.Timedelta(days=1)

if __name__ == "__main__":
    main()