#!/usr/bin/env python3
"""Small NOAA CDO client example.

Reads `NOAA_API_KEY` from the environment and performs a simple GET request
against the NOAA CDO API. Do NOT store your token in source control.

Note: This script will try to load a local `.env` file using `python-dotenv`
if that package is installed. Install dependencies:

    pip install requests python-dotenv

"""
import os
import time
from typing import Optional, Dict, Any

import requests

# Try to load `.env` automatically for local development (no dependency required)
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # If python-dotenv isn't installed, we simply rely on the environment.
    pass


def get_noaa_data(endpoint: str, params: Optional[Dict[str, Any]] = None, token: Optional[str] = None,
                  retries: int = 3, backoff: float = 1.0) -> Dict[str, Any]:
    """Fetch JSON from NOAA CDO API `endpoint` (e.g. 'stations' or 'data').

    The NOAA CDO API expects the API token in the `token` header.
    """
    token = token or os.getenv("NOAA_API_KEY")
    if not token:
        raise RuntimeError("NOAA API token not found. Set NOAA_API_KEY environment variable.")

    headers = {"token": token}
    url = f"https://www.ncdc.noaa.gov/cdo-web/api/v2/{endpoint.lstrip('/') }"

    for attempt in range(retries):
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            time.sleep(backoff * (2 ** attempt))
            continue
        resp.raise_for_status()

    raise RuntimeError("Failed to fetch NOAA data after retries")


if __name__ == "__main__":
    # Quick standalone example (no key printed)
    try:
        # Example: list stations for dataset GHCND (daily summaries)
        example = get_noaa_data("stations", params={"datasetid": "GHCND", "limit": 5})
        print("Received station list (keys):", list(example.keys()))
    except Exception as e:
        print("NOAA client error:", e)
