#!/usr/bin/env python3
"""NASA POWER API client for environmental sensor data.

This module fetches temperature, humidity, pressure, and solar radiation data
from NASA's POWER API (https://power.larc.nasa.gov/api/).

Public data endpoints require no authentication; restricted data requires
Earthdata login credentials (username/password or token).

Usage:
    # Public data (no auth needed)
    data = get_power_data(
        latitude=38.0, longitude=-77.0,
        start_date="20210101", end_date="20210131",
        temporal_api="daily",
        parameters=["T2M", "RH2M", "ALLSKY_SFC_SW_DWN"]
    )

    # Restricted data (if needed)
    data = get_power_data(
        latitude=38.0, longitude=-77.0,
        start_date="20210101", end_date="20210131",
        temporal_api="hourly",
        parameters=["T2M"],
        username="your_earthdata_username",
        password="your_earthdata_password"
    )
"""
import os
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

# Try to load `.env` automatically for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


BASE_URL = "https://power.larc.nasa.gov/api/"


def get_power_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    temporal_api: str = "daily",
    parameters: Optional[List[str]] = None,
    data_format: str = "JSON",
    community: str = "SB",
    username: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 60,
    retries: int = 3,
) -> Dict[str, Any]:
    """Fetch data from NASA POWER API.

    Args:
        latitude: Latitude (-90 to 90).
        longitude: Longitude (-180 to 180).
        start_date: Start date in YYYYMMDD format (e.g. "20210101").
        end_date: End date in YYYYMMDD format (e.g. "20210131").
        temporal_api: One of "hourly", "daily", "monthly", "climatology". Defaults to "daily".
        parameters: List of parameter names (e.g. ["T2M", "ALLSKY_SFC_SW_DWN"]).
                    See https://power.larc.nasa.gov/docs/services/api/temporal/hourly/
        data_format: Response format ("JSON", "CSV", "netcdf"). Defaults to "JSON".
        community: Community code ("SB" = Single Point, "AG" = Agriculture, etc.). Defaults to "SB".
        username: Earthdata username (for restricted data). Optional for public data.
        password: Earthdata password (for restricted data). Optional for public data.
        timeout: Request timeout in seconds.
        retries: Number of retry attempts.

    Returns:
        Parsed JSON response (or raw text if format != JSON).

    Raises:
        RuntimeError: If request fails after retries.
    """
    if parameters is None:
        parameters = ["T2M", "ALLSKY_SFC_SW_DWN", "RH2M", "PS"]

    # Build endpoint URL
    endpoint = f"temporal/{temporal_api}/point"
    url = urljoin(BASE_URL, endpoint)

    # Build query parameters (use longitude/latitude, not lon/lat)
    params = {
        "start": start_date,
        "end": end_date,
        "latitude": latitude,
        "longitude": longitude,
        "parameters": ",".join(parameters),
        "format": data_format,
        "community": community,
    }

    auth = None
    if username and password:
        auth = HTTPBasicAuth(username, password)

    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, auth=auth, timeout=timeout)
            if resp.status_code == 200:
                if data_format == "JSON":
                    return resp.json()
                else:
                    return {"raw": resp.text}
            elif resp.status_code == 429:
                # Rate limit; backoff and retry
                import time
                time.sleep(2 ** attempt)
                continue
            else:
                resp.raise_for_status()
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Failed to fetch NASA POWER data: {e}") from e
            continue

    raise RuntimeError("Failed to fetch NASA POWER data after retries")


if __name__ == "__main__":
    # Quick example: fetch daily temperature and humidity for a point
    try:
        print("Fetching NASA POWER data for point (38.0, -77.0) from Jan 2021...")
        data = get_power_data(
            latitude=38.0,
            longitude=-77.0,
            start_date="20210101",
            end_date="20210110",
            temporal_api="daily",
            parameters=["T2M", "RH2M", "ALLSKY_SFC_SW_DWN"],
        )
        print("Success! Response keys:", list(data.keys()))
        if "properties" in data:
            print("Properties:", list(data.get("properties", {}).keys()))
    except Exception as e:
        print(f"Error: {e}")
