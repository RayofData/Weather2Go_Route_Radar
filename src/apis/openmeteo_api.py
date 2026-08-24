"""Sets up clients for OpenMeteo API requests."""

from pathlib import Path

import openmeteo_requests
import requests_cache
from retry_requests import retry


FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"

CACHE_PATH = Path(".cache") / "openmeteo"

openmeteo = openmeteo_requests.Client()

def build_historical_client():
    """Create an Open-Meteo client with caching and retries."""
    cache_session = requests_cache.CachedSession(
        CACHE_PATH,
        expire_after=-1
    )

    retry_session = retry(
        cache_session,
        retries=5,
        backoff_factor=0.2
    )

    return openmeteo_requests.Client(session=retry_session)
